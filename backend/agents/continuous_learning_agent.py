import uuid
from datetime import datetime
from pydantic import BaseModel

from agents.base_agent import BaseAgent
from repositories.campaign_repository import CampaignRepository
from repositories.trend_repository import TrendRepository
from schemas.universal_content import UniversalContent
from schemas.brand_identity import BrandIdentityModel
from schemas.trend_knowledge import TrendKnowledge
from schemas.campaign_memory import CampaignMemory
from schemas.drift_report import DriftReport
from schemas.prediction_report import PredictionReport
from utils.logger import get_logger

logger = get_logger(__name__)


class ContinuousLearningInput(BaseModel):
    company_id: str
    content: UniversalContent | None = None
    brand_identity: BrandIdentityModel | None = None
    trend_knowledge: TrendKnowledge | None = None
    drift_report: DriftReport | None = None
    prediction_report: PredictionReport | None = None


class ContinuousLearningAgent(BaseAgent):
    name = "continuous_learning"

    def __init__(self):
        self._campaign_repo = CampaignRepository()
        self._trend_repo = TrendRepository()

    async def run(self, input_data: ContinuousLearningInput) -> CampaignMemory | None:
        """Record campaign memory from this ingest cycle."""
        if input_data.content is None:
            logger.info("Continuous learning: no content to record.")
            return None

        campaign = CampaignMemory(
            campaign_id=str(uuid.uuid4()),
            company_id=input_data.company_id,
            content_ids=[input_data.content.content_id],
            performance_actuals=None,
            drift_report_id=input_data.drift_report.report_id if input_data.drift_report else None,
            prediction_report_id=input_data.prediction_report.report_id if input_data.prediction_report else None,
            created_at=datetime.utcnow(),
        )
        await self._campaign_repo.save(campaign)
        logger.info("Continuous learning: saved campaign memory %s", campaign.campaign_id)
        return campaign
