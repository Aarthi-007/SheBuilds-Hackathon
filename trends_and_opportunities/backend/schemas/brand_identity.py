from datetime import datetime
from pydantic import BaseModel


class BrandIdentityModel(BaseModel):
    company_id: str
    industry: str
    tone: list[str]
    core_values: list[str]
    personality_traits: list[str]
    messaging_pillars: list[str]
    target_audience: dict
    visual_identity: dict
    historical_campaign_ids: list[str]
    version: int
    updated_at: datetime
