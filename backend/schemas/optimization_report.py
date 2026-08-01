from pydantic import BaseModel, Field
from datetime import datetime


class OptimizationReport(BaseModel):
    report_id: str
    content_id: str
    original_text: str
    optimized_text: str
    diff_explanation: str
    identity_preserved: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)
