from pydantic import BaseModel, Field
from datetime import datetime


class CampaignMemory(BaseModel):
    campaign_id: str
    company_id: str
    content_ids: list[str]
    performance_actuals: dict | None = None
    drift_report_id: str | None = None
    prediction_report_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
