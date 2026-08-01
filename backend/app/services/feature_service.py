import os
import hashlib
import logging
from typing import List, Dict, Any, Optional
from app.models.feature_store import FeatureStore

logger = logging.getLogger("uvicorn")


class FeatureStoreService:
    """
    Feature Store Service for Klyros.
    
    Responsibilities:
    - SHA-256 asset hash generation & AI inference caching.
    - Storing raw extracted features into `feature_store` collection.
    - Providing normalized feature records for Brand Identity Builder.
    """

    @staticmethod
    def compute_asset_hash(file_path: str, fallback_identifier: str = "") -> str:
        """Compute SHA-256 checksum of an asset file for AI inference caching."""
        if os.path.exists(file_path):
            try:
                hasher = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        hasher.update(chunk)
                return hasher.hexdigest()
            except Exception as e:
                logger.error("Error computing SHA-256 for file %s: %s", file_path, e)
        
        return hashlib.sha256((fallback_identifier or file_path).encode("utf-8")).hexdigest()

    @classmethod
    async def get_cached_features_async(cls, asset_hash: str) -> List[FeatureStore]:
        """Check AI cache: If asset_hash exists in feature_store, return cached features."""
        if not asset_hash:
            return []
        try:
            cached = await FeatureStore.find(FeatureStore.asset_hash == asset_hash).to_list()
            return cached
        except Exception as e:
            logger.error("Error querying Feature Store cache for hash %s: %s", asset_hash, e)
            return []

    @classmethod
    async def store_features_async(
        cls,
        brand_id: str,
        asset_id: str,
        asset_type: str,
        asset_hash: str,
        features: List[Dict[str, Any]]
    ) -> List[FeatureStore]:
        """
        Store extracted features into the `feature_store` MongoDB collection.
        Each feature record contains feature_name, value, confidence, source_model, evidence.
        """
        stored_records = []
        for feat in features:
            try:
                record = FeatureStore(
                    asset_id=asset_id,
                    brand_id=brand_id,
                    asset_type=asset_type,
                    asset_hash=asset_hash,
                    feature_name=feat.get("feature_name", "general_feature"),
                    value=feat.get("value", ""),
                    confidence=float(feat.get("confidence", 95.0)),
                    model=feat.get("model", feat.get("source_model", "qwen")),
                    source_model=feat.get("source_model", feat.get("model", "qwen")),
                    source=feat.get("source", asset_type),
                    evidence=feat.get("evidence", ""),
                    processing_time=float(feat.get("processing_time_ms", feat.get("processing_time", 0.0)))
                )
                await record.insert()
                stored_records.append(record)
            except Exception as e:
                logger.error("Error inserting FeatureStore record: %s", e)

        return stored_records

    @classmethod
    async def get_brand_features_async(cls, brand_id: str) -> List[FeatureStore]:
        """Retrieve all extracted feature records for a given brand."""
        try:
            return await FeatureStore.find(FeatureStore.brand_id == brand_id).to_list()
        except Exception as e:
            logger.error("Error fetching FeatureStore records for brand %s: %s", brand_id, e)
            return []
