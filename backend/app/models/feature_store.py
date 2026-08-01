from datetime import datetime, timezone
from typing import Optional, Any
from beanie import Document, Indexed
from pydantic import Field


class FeatureStore(Document):
    asset_id: Indexed(str)
    brand_id: Indexed(str)
    asset_type: str  # image, audio, video, pdf, website, text
    asset_hash: Indexed(str)  # SHA-256 checksum for AI caching
    feature_name: str  # dominant_colors, brand_voice, tone, transcript, cta, etc.
    value: Any  # Normalized feature value (dict, list, str, float)
    confidence: float = 95.0  # 0 to 100 confidence score
    model: str = "qwen"  # qwen, whisper, ocr, pymupdf, sentence_transformer
    source_model: Optional[str] = None  # provider/version name
    source: str = "asset"  # asset type or origin
    evidence: Optional[str] = None  # Text/visual evidence supporting feature
    processing_time: float = 0.0  # processing time in ms
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "feature_store"
