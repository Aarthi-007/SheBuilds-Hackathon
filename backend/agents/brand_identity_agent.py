import uuid
import json
from datetime import datetime
from pydantic import BaseModel

from agents.base_agent import BaseAgent
from services.claude_service import ClaudeService
from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService
from repositories.brand_repository import BrandRepository
from schemas.brand_identity import BrandIdentityModel
from schemas.universal_content import UniversalContent
from config.settings import settings


class BrandIdentityInput(BaseModel):
    company_id: str
    content_batch: list[UniversalContent]


class BrandIdentityAgent(BaseAgent):
    name = "brand_identity"

    def __init__(self):
        self._claude = ClaudeService()
        self._embed = EmbeddingService()
        self._pinecone = PineconeService()
        self._repo = BrandRepository()

    async def run(self, input_data: BrandIdentityInput) -> BrandIdentityModel:
        batch_dicts = [c.model_dump() for c in input_data.content_batch]

        # Extract brand identity via Claude
        raw = await self._claude.extract_brand_identity(batch_dicts, input_data.company_id)

        # Get existing version for incrementing
        existing = await self._repo.get_by_company(input_data.company_id)
        version = (existing.version + 1) if existing else 1

        model = BrandIdentityModel(
            company_id=input_data.company_id,
            industry=raw.get("industry", "unknown"),
            tone=raw.get("tone", []),
            core_values=raw.get("core_values", []),
            personality_traits=raw.get("personality_traits", []),
            messaging_pillars=raw.get("messaging_pillars", []),
            target_audience=raw.get("target_audience", {}),
            visual_identity=raw.get("visual_identity", {}),
            historical_campaign_ids=raw.get("historical_campaign_ids", []),
            version=version,
            updated_at=datetime.utcnow(),
        )

        # Persist to MongoDB
        await self._repo.save(model)

        # Embed brand identity summary and upsert to Pinecone
        summary = self._build_summary(model)
        vector = self._embed.embed(summary)
        self._pinecone.upsert(
            index_name=settings.pinecone_index_brand,
            namespace=model.company_id,
            vector_id=model.company_id,
            vector=vector,
            metadata={
                "company_id": model.company_id,
                "version": model.version,
                "updated_at": model.updated_at.isoformat(),
            },
        )

        return model

    def _build_summary(self, model: BrandIdentityModel) -> str:
        return (
            f"Industry: {model.industry}. "
            f"Tone: {', '.join(model.tone)}. "
            f"Values: {', '.join(model.core_values)}. "
            f"Messaging: {', '.join(model.messaging_pillars)}. "
            f"Personality: {', '.join(model.personality_traits)}."
        )
