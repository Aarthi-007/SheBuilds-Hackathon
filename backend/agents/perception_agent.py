import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Literal

from agents.base_agent import BaseAgent
from services.groq_service import GroqService
from services.claude_service import ClaudeService
from utils.json_flatten import flatten_dict
from schemas.universal_content import UniversalContent


class PerceptionInput(BaseModel):
    content_id: str | None = None
    company_id: str
    modality: Literal["text", "image", "video"]
    payload: str  # raw text or base64


class PerceptionAgent(BaseAgent):
    name = "perception"

    def __init__(self):
        self._groq = GroqService()
        self._claude = ClaudeService()

    async def run(self, input_data: PerceptionInput) -> UniversalContent:
        content_id = input_data.content_id or str(uuid.uuid4())

        # Step 1: Groq multimodal perception
        structured = await self._groq.perceive(input_data.payload, input_data.modality)

        # Step 2: Claude semantic enrichment
        semantic = await self._claude.enrich_perception(structured)

        # Step 3: Flatten for embedding
        combined = {"structured": structured, "semantic": semantic}
        flattened = flatten_dict(combined)

        return UniversalContent(
            content_id=content_id,
            company_id=input_data.company_id,
            modality=input_data.modality,
            raw_reference=input_data.payload[:512],  # store first 512 chars as reference
            structured_description=structured,
            semantic_layer=semantic,
            flattened_text=flattened,
            created_at=datetime.utcnow(),
        )
