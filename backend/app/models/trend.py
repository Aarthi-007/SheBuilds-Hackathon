from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field

class TrendReport(Document):
    brand_id: Indexed(str)
    trend: str
    category: str
    alignment_score: float
    trend_score: float
    competition_score: float
    forecast_score: Optional[float] = 92.0
    recommended_platform: str = "Instagram"
    best_posting_time: str = "19:00"
    generated_campaign: Dict[str, Any] = Field(default_factory=dict)
    hashtags: List[str] = Field(default_factory=list)
    status: str = "recommended"  # recommended, saved, dismissed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "trend_reports"
