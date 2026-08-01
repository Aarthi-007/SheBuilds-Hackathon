from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field

class OptimizationReport(Document):
    campaign_id: Indexed(str)
    campaign_version_id: str
    original_version: int
    optimized_version: int
    validation_score_before: float
    validation_score_after: float
    overall_improvement: float
    changes: List[Dict[str, Any]] = Field(default_factory=list)
    multi_versions: List[Dict[str, Any]] = Field(default_factory=list)  # Version A (Brand Consistency), B (Engagement), C (Creativity)
    status: str = "completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "optimization_reports"
