from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ValidationCheckRequest(BaseModel):
    brand_id: str
    campaign_id: Optional[str] = None
    text_content: str
    image_url: Optional[str] = None
    platform: str = "Instagram"
    objective: str = "Brand Engagement"

class IssueDTO(BaseModel):
    category: str
    severity: str  # High, Medium, Low
    message: str
    solution: Optional[str] = None

class ValidationReportDTO(BaseModel):
    id: str
    campaign_id: str
    brand_id: str
    overall_score: float
    status: str
    scores: Dict[str, float]
    issues: List[IssueDTO]
    recommendations: List[str]
    created_at: str
