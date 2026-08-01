from pydantic import BaseModel, Field
from datetime import datetime


class ComplianceReport(BaseModel):
    report_id: str
    content_id: str
    passed: bool
    violations: list[str]
    notes: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
