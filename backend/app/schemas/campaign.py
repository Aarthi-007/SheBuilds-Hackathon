from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class CampaignCreateRequest(BaseModel):
    brand_id: str
    title: str
    description: Optional[str] = None
    platform: str = "Instagram"
    objective: str = "Brand Engagement"
    text_content: Optional[str] = ""

class CampaignDTO(BaseModel):
    id: str
    brand_id: str
    title: str
    description: Optional[str]
    platform: str
    objective: str
    status: str
    current_version: int
    published: bool
    created_at: str

class CampaignVersionDTO(BaseModel):
    id: str
    campaign_id: str
    version: int
    text_content: str
    image_urls: List[str]
    video_urls: List[str]
    generated_by: str
    validation_score: Optional[float]
    approved: bool
    created_at: str
