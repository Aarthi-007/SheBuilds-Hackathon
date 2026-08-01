from pydantic import BaseModel, Field
from datetime import datetime


class DriftReport(BaseModel):
    report_id: str
    content_id: str
    company_id: str
    drift_score: float
    brand_similarity: float
    competitor_similarity: dict[str, float]
    distinctiveness_score: float
    explanation: str
    recommendations: list[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
