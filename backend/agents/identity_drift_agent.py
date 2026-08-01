import uuid
import json
from datetime import datetime
from pydantic import BaseModel

from agents.base_agent import BaseAgent
from services.claude_service import ClaudeService
from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService
from services.scoring_service import ScoringService
from schemas.universal_content import UniversalContent
from schemas.brand_identity import BrandIdentityModel
from schemas.drift_report import DriftReport
from config.settings import settings


class DriftInput(BaseModel):
    content: UniversalContent
    brand_identity: BrandIdentityModel


class IdentityDriftAgent(BaseAgent):
    name = "drift"

    def __init__(self):
        self._claude = ClaudeService()
        self._embed = EmbeddingService()
        self._pinecone = PineconeService()
        self._scoring = ScoringService()

    async def run(self, input_data: DriftInput) -> DriftReport:
        content = input_data.content
        brand = input_data.brand_identity

        # Embed content
        content_vector = self._embed.embed(content.flattened_text)

        # Query brand identity similarity
        brand_matches = self._pinecone.query(
            index_name=settings.pinecone_index_brand,
            namespace=content.company_id,
            vector=content_vector,
            top_k=1,
        )
        brand_similarity = brand_matches[0]["score"] if brand_matches else 0.0

        # Query competitor similarity
        competitor_matches = self._pinecone.query(
            index_name=settings.pinecone_index_competitor,
            namespace=content.company_id,
            vector=content_vector,
            top_k=10,
        )
        competitor_similarity = {
            m["metadata"].get("competitor_id", m["id"]): m["score"]
            for m in competitor_matches
        }

        # Compute scores
        drift_score = self._scoring.compute_drift_score(
            brand_similarity, list(competitor_similarity.values())
        )
        distinctiveness = self._scoring.compute_distinctiveness(
            brand_similarity, list(competitor_similarity.values())
        )

        # Claude generates explanation
        variables = {
            "drift_score": drift_score,
            "brand_similarity": brand_similarity,
            "competitor_similarity": json.dumps(competitor_similarity),
            "distinctiveness_score": distinctiveness,
            "brand_identity": json.dumps(brand.model_dump()),
            "content_text": content.flattened_text[:2000],
        }
        result = await self._claude.generate_structured(
            "identity_drift_explanation.md", variables, _DriftExplanation
        )

        return DriftReport(
            report_id=str(uuid.uuid4()),
            content_id=content.content_id,
            company_id=content.company_id,
            drift_score=drift_score,
            brand_similarity=brand_similarity,
            competitor_similarity=competitor_similarity,
            distinctiveness_score=distinctiveness,
            explanation=result.explanation,
            recommendations=result.recommendations,
            created_at=datetime.utcnow(),
        )


class _DriftExplanation(BaseModel):
    explanation: str
    recommendations: list[str]
