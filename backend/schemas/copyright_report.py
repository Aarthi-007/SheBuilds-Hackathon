from pydantic import BaseModel, Field
from datetime import datetime


class CopyrightReport(BaseModel):
    report_id: str
    content_id: str
    plagiarism_flag: bool
    trademark_conflicts: list[str]
    sources_matched: list[str]
    notes: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
