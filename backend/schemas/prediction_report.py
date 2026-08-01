from pydantic import BaseModel, Field
from datetime import datetime


class PredictionReport(BaseModel):
    report_id: str
    content_id: str
    predicted_engagement: float
    predicted_reach: float
    predicted_ctr: float
    predicted_virality: float
    reasoning: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
