import uuid
import json
from datetime import datetime
from pydantic import BaseModel

from agents.base_agent import BaseAgent
from services.claude_service import ClaudeService
from schemas.universal_content import UniversalContent
from schemas.brand_identity import BrandIdentityModel
from schemas.drift_report import DriftReport
from schemas.prediction_report import PredictionReport
from schemas.optimization_report import OptimizationReport


class OptimizationInput(BaseModel):
    content: UniversalContent
    brand_identity: BrandIdentityModel
    drift_report: DriftReport | None = None
    prediction_report: PredictionReport | None = None


class OptimizationAgent(BaseAgent):
    name = "optimization"

    def __init__(self):
        self._claude = ClaudeService()

    async def run(self, input_data: OptimizationInput) -> OptimizationReport:
        original_text = input_data.content.flattened_text

        variables = {
            "original_text": original_text[:3000],
            "brand_identity": json.dumps(input_data.brand_identity.model_dump()),
            "drift_score": input_data.drift_report.drift_score if input_data.drift_report else "N/A",
            "drift_recommendations": json.dumps(
                input_data.drift_report.recommendations if input_data.drift_report else []
            ),
            "predicted_engagement": input_data.prediction_report.predicted_engagement if input_data.prediction_report else "N/A",
            "predicted_virality": input_data.prediction_report.predicted_virality if input_data.prediction_report else "N/A",
        }

        result = await self._claude.generate_structured(
            "optimization_rewrite.md", variables, _OptimizationOutput
        )

        return OptimizationReport(
            report_id=str(uuid.uuid4()),
            content_id=input_data.content.content_id,
            original_text=original_text,
            optimized_text=result.optimized_text,
            diff_explanation=result.diff_explanation,
            identity_preserved=result.identity_preserved,
            created_at=datetime.utcnow(),
        )


class _OptimizationOutput(BaseModel):
    optimized_text: str
    diff_explanation: str
    identity_preserved: bool
    preserved_elements: list[str] = []
