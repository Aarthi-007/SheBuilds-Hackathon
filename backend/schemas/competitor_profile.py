from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class CompetitorProfile(BaseModel):
    competitor_id: str
    company_id: str
    name: str
    tier: Literal["primary", "secondary", "emerging"]
    industry: str
    tone: list[str]
    messaging_pillars: list[str]
    sample_content_refs: list[str]
    last_scanned_at: datetime
