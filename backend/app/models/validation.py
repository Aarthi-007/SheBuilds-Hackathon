from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field

class ValidationReport(Document):
    campaign_id: Indexed(str)
    campaign_version_id: str
    brand_id: Indexed(str)
    overall_score: float
    status: str  # approved, needs_review, rejected
    scores: Dict[str, float] = Field(default_factory=dict)
    # scores: identity (35%), visual (20%), compliance (15%), copyright (10%), safety (10%), context (10%)
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "validation_reports"
