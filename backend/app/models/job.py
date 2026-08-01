from datetime import datetime, timezone
from typing import Optional, Dict, Any
from beanie import Document, Indexed
from pydantic import Field

class Job(Document):
    brand_id: Indexed(str)
    job_type: str  # Identity, Validation, Optimization, Trend, Embedding, OCR
    status: str = "queued"  # queued, processing, completed, failed
    progress: int = 0  # 0 to 100
    current_stage: str = "Initiated"
    result_reference: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    class Settings:
        name = "jobs"

class AuditLog(Document):
    user_id: Indexed(str)
    action: str
    resource: str
    resource_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "audit_logs"
