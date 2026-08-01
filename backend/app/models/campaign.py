from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from beanie import Document, Indexed
from pydantic import Field

class Campaign(Document):
    brand_id: Indexed(str)
    title: str
    description: Optional[str] = None
    platform: str = "Instagram"  # Instagram, LinkedIn, X, Facebook, Multi
    objective: str = "Brand Awareness"
    status: str = "draft"  # draft, validating, optimizing, certified, published
    current_version: int = 1
    published: bool = False
    published_at: Optional[datetime] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "campaigns"

class CampaignVersion(Document):
    campaign_id: Indexed(str)
    version: int = 1
    text_content: str
    image_urls: List[str] = Field(default_factory=list)
    video_urls: List[str] = Field(default_factory=list)
    generated_by: str = "AI Engine"  # AI Engine, Human Edit, Optimizer
    validation_score: Optional[float] = None
    approved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "campaign_versions"
