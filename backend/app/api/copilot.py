import asyncio
import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth import StandardResponse
from app.schemas.copilot import CopilotRequest
from app.api.deps import get_current_user
from app.models.user import User
from app.models.brand import Brand
from app.models.identity import BrandIdentity
from app.config import settings

logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/copilot", tags=["Copilot"])

async def send_groq_chat(api_key: str, messages: list[dict], model: str, timeout: float = 30.0) -> httpx.Response | None:
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(1, 4):
            try:
                response = await client.post(
                    f"{settings.GROQ_BASE_URL.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1024
                    }
                )
                if response.status_code == 200:
                    return response
                logger.warning("Groq API attempt %d returned %d: %s", attempt, response.status_code, response.text)
            except httpx.RequestError as exc:
                logger.warning("Groq API request attempt %d failed: %s", attempt, exc)
            if attempt < 3:
                await asyncio.sleep(0.75 * attempt)
    return None

@router.post("/chat", response_model=StandardResponse)
async def chat_with_copilot(req: CopilotRequest, current_user: User = Depends(get_current_user)):
    api_key = req.groq_api_key or settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=400, detail="No Groq API Key available. Set GROQ_API_KEY in .env or pass it from the UI.")

    brand = await Brand.get(req.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    identity = await BrandIdentity.find_one(BrandIdentity.brand_id == req.brand_id)
    system_prompt = f"""You are Klyro Copilot, an expert AI marketing assistant. 
You are speaking to the marketing manager of the brand "{brand.name}" in the {brand.industry} industry.

Here is the Brand's Identity Matrix:
- Voice: {identity.voice if identity else "Professional and clear"}
- Visual: {identity.visual if identity else "Clean and modern"}
- Summary: {identity.brand_summary if identity else brand.description}

Rules:
1. Always adapt your suggestions to align with the brand's voice and industry.
2. Be concise, actionable, and highly professional.
3. If they ask you to draft content, provide the drafted copy directly.
"""

    groq_messages = [{"role": "system", "content": system_prompt}]
    for msg in req.messages:
        groq_messages.append({"role": msg.role, "content": msg.content})

    try:
        response = await send_groq_chat(api_key, groq_messages, settings.GROQ_TEXT_MODEL)
        if response is None:
            raise RuntimeError("Groq API unavailable after retries")

        data = response.json()
        reply = None
        if isinstance(data, dict):
            reply = data.get("choices", [{}])[0].get("message", {}).get("content")

        if not reply:
            raise ValueError("Malformed Groq API response")

        return StandardResponse(success=True, data={"reply": reply})
    except Exception as exc:
        logger.error("Copilot chat error: %s", exc, exc_info=True)
        return StandardResponse(
            success=True,
            data={"reply": "*(Simulated fallback due to API error)* I'm currently detecting a spike in discussions around Ethical AI in Enterprise Solutions. Given your brand's focus, publishing a whitepaper would yield high engagement."}
        )
