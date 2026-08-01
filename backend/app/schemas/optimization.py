from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class OptimizationRunRequest(BaseModel):
    campaign_id: str
    campaign_version_id: Optional[str] = None
    target_tone: Optional[str] = None

class OptimizationReportDTO(BaseModel):
    id: str
    campaign_id: str
    campaign_version_id: str
    original_version: int
    optimized_version: int
    validation_score_before: float
    validation_score_after: float
    overall_improvement: float
    changes: List[Dict[str, Any]]
    multi_versions: List[Dict[str, Any]]
    status: str
