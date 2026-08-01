from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class DiscoverTrendsRequest(BaseModel):
    brand_id: str
    category: Optional[str] = None

class GenerateTrendCampaignRequest(BaseModel):
    brand_id: str
    trend_name: str
    target_platform: str = "Instagram"

class TrendReportDTO(BaseModel):
    id: str
    brand_id: str
    trend: str
    category: str
    alignment_score: float
    trend_score: float
    competition_score: float
    forecast_score: float
    recommended_platform: str
    best_posting_time: str
    generated_campaign: Dict[str, Any]
    hashtags: List[str]
    status: str
