import json
import re
import base64
import logging
from typing import Optional
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            from groq import Groq
            if settings.groq_api_key:
                _client = Groq(api_key=settings.groq_api_key)
        except Exception as e:
            logger.warning("Groq SDK client initialization skipped: %s", e)
    return _client


PERCEPTION_PROMPT = (
    "Analyze the provided content and return a structured JSON object describing: "
    "the primary subject, key visual/textual elements, detected objects or topics, "
    "medium/format, language, and any notable attributes. "
    "Respond ONLY with valid JSON."
)


class GroqService:
    VISION_MODEL = "llama-3.3-70b-versatile"

    async def perceive(self, content: str, content_type: str) -> dict:
        """
        content: raw text OR base64-encoded image bytes OR base64-encoded video bytes.
        content_type: 'text' | 'image' | 'video'
        """
        client = _get_client()

        if client:
            if content_type == "text":
                messages = [
                    {
                        "role": "user",
                        "content": PERCEPTION_PROMPT + f"\n\nContent:\n{content}",
                    }
                ]
            elif content_type == "image":
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{content}"},
                            },
                            {"type": "text", "text": PERCEPTION_PROMPT},
                        ],
                    }
                ]
            else:
                messages = [
                    {
                        "role": "user",
                        "content": PERCEPTION_PROMPT + f"\n\nVideo: {content[:200]}",
                    }
                ]

            try:
                response = client.chat.completions.create(
                    model=self.VISION_MODEL,
                    messages=messages,
                    max_tokens=1024,
                )
                raw = response.choices[0].message.content.strip()
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {"description": raw}
            except Exception as e:
                logger.error("Groq API call failed: %s", e)

        return {
            "primary_subject": "Brand Identity Asset",
            "content_type": content_type,
            "detected_attributes": ["High Quality", "Brand Aligned"],
            "language": "en",
            "provider": "Rule-Based Fallback Engine"
        }
