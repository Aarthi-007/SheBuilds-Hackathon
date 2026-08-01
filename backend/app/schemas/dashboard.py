from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class MetricCard(BaseModel):
    title: str
    value: Any
    change: Optional[str] = None
    icon: Optional[str] = None

class DashboardSummaryDTO(BaseModel):
    total_brands: int
    total_campaigns: int
    avg_certification_score: float
    active_trends_count: int
    metrics: List[MetricCard]
    recent_activities: List[Dict[str, Any]]
    recent_campaigns: List[Dict[str, Any]]
    top_aligned_trends: List[Dict[str, Any]]
