from pydantic import BaseModel, Field
from datetime import datetime


class SafetyReport(BaseModel):
    report_id: str
    content_id: str
    toxicity_flag: bool
    bias_flag: bool
    misinformation_flag: bool
    notes: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
