import uuid
import json
from datetime import datetime
from pydantic import BaseModel

from agents.base_agent import BaseAgent
from services.claude_service import ClaudeService
from services.scoring_service import ScoringService
from schemas.universal_content import UniversalContent
from schemas.brand_identity import BrandIdentityModel
from schemas.drift_report import DriftReport
from schemas.prediction_report import PredictionReport


class PredictionInput(BaseModel):
    content: UniversalContent
    brand_identity: BrandIdentityModel
    drift_report: DriftReport | None = None
    historical_performance: dict | None = None
    trend_alignment: float = 0.5


class PredictiveIntelligenceAgent(BaseAgent):
    name = "prediction"

    def __init__(self):
        self._claude = ClaudeService()
        self._scoring = ScoringService()

    async def run(self, input_data: PredictionInput) -> PredictionReport:
        features = self._scoring.compute_prediction_features(
            drift_score=input_data.drift_report.drift_score if input_data.drift_report else 0.5,
            brand_similarity=input_data.drift_report.brand_similarity if input_data.drift_report else 0.5,
            trend_alignment=input_data.trend_alignment,
        )

        variables = {
            "content_text": input_data.content.flattened_text[:2000],
            "brand_identity": json.dumps(input_data.brand_identity.model_dump()),
            "prediction_features": json.dumps(features),
            "historical_performance": json.dumps(input_data.historical_performance or {}),
            "trend_alignment": input_data.trend_alignment,
        }

        result = await self._claude.generate_structured(
            "prediction_reasoning.md", variables, _PredictionOutput
        )

        return PredictionReport(
            report_id=str(uuid.uuid4()),
            content_id=input_data.content.content_id,
            predicted_engagement=result.predicted_engagement,
            predicted_reach=result.predicted_reach,
            predicted_ctr=result.predicted_ctr,
            predicted_virality=result.predicted_virality,
            reasoning=result.reasoning,
            created_at=datetime.utcnow(),
        )


class _PredictionOutput(BaseModel):
    predicted_engagement: float
    predicted_reach: float
    predicted_ctr: float
    predicted_virality: float
    reasoning: str
