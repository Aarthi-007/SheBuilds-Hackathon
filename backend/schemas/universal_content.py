from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class UniversalContent(BaseModel):
    content_id: str
    company_id: str
    modality: Literal["text", "image", "video"]
    raw_reference: str
    structured_description: dict
    semantic_layer: dict
    flattened_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
