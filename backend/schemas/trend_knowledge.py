from pydantic import BaseModel, Field
from datetime import datetime


class TrendKnowledge(BaseModel):
    company_id: str
    industry_trends: list[str]
    emerging_topics: list[str]
    competitor_campaigns: list[dict]
    trending_hashtags: list[str]
    seasonal_events: list[dict]
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
