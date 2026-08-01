from pydantic import BaseModel, Field
from datetime import datetime


class BrandIdentityModel(BaseModel):
    company_id: str
    industry: str
    tone: list[str]
    core_values: list[str]
    personality_traits: list[str]
    messaging_pillars: list[str]
    target_audience: dict
    visual_identity: dict
    historical_campaign_ids: list[str] = Field(default_factory=list)
    version: int = 1
    updated_at: datetime = Field(default_factory=datetime.utcnow)
