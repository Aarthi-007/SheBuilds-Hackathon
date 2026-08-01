from datetime import datetime, timezone
from typing import Optional, Any
from beanie import Document, Indexed
from pydantic import Field


class FeatureStore(Document):
    asset_id: Indexed(str)
    brand_id: Indexed(str)
    asset_type: str  # image, audio, video, pdf, website, text
    asset_hash: Indexed(str)  # SHA-256 checksum for AI caching
    feature_name: str  # brand_voice, color_system, typography, audio_transcript, frame_concept, etc.
    value: Any  # Normalized feature value (dict, list, str, float)
    confidence: float = 95.0  # 0 to 100 confidence score
    source_model: str  # qwen2.5-vl, whisper-tiny, pymupdf, paddleocr, bge-m3, groq
    evidence: Optional[str] = None  # Text/visual evidence supporting feature
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "feature_store"
