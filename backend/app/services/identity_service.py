from typing import Optional, Dict, Any, Tuple, List
from collections import Counter
from fastapi import HTTPException, status
from app.models.brand import Brand, BrandAsset
from app.models.identity import BrandIdentity, AIMemory
from app.models.feature_store import FeatureStore
from app.models.job import Job
from app.ai.multimodal_analyzer import MultimodalAnalyzer
from app.services.feature_service import FeatureStoreService


class IdentityService:
    """
    Brand Identity Builder Service.
    
    CRITICAL RULE:
    The Brand Identity Builder NEVER consumes raw AI outputs directly.
    It ONLY consumes normalized FeatureStore records.
    
    Responsibilities:
    - Trigger feature extraction into FeatureStore for all assets.
    - Read normalized FeatureStore records.
    - Cluster features, resolve conflicts, vote by confidence, calculate consensus.
    - Synthesize and persist the Living Brand Identity model.
    """

    @classmethod
    async def build_identity(
        cls,
        brand_id: str,
        org_id: str,
        force_rebuild: bool = False,
        groq_api_key: Optional[str] = None
    ) -> Tuple[BrandIdentity, Job]:
        brand = await Brand.get(brand_id)
        if not brand or brand.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        assets = await BrandAsset.find({"brand_id": brand_id}).to_list()

        # Step 1: Run Multimodal Feature Extraction into Feature Store for all assets
        for asset in assets:
            asset_dict = {
                "id": str(asset.id),
                "asset_type": asset.asset_type,
                "mime_type": asset.mime_type,
                "storage_path": asset.storage_path,
                "filename": asset.asset_name,
                "metadata": asset.metadata
            }
            await MultimodalAnalyzer.extract_and_store_features_async(
                brand_id=brand_id,
                asset=asset_dict,
                api_key=groq_api_key
            )
            asset.processing_status = "completed"
            await asset.save()

        # Step 2: Read ONLY from Feature Store (perception decoupled from reasoning)
        feature_records: List[FeatureStore] = await FeatureStoreService.get_brand_features_async(brand_id)

        # Step 3: Cluster features, resolve conflicts, and vote by confidence
        synthesized_identity = cls._synthesize_from_feature_store(brand.name, feature_records, len(assets))

        # Step 4: Persist Living Brand Identity in MongoDB
        existing_identity = await BrandIdentity.find_one({"brand_id": brand_id})

        if existing_identity:
            existing_identity.version += 1
            existing_identity.voice = synthesized_identity["voice"]
            existing_identity.visual = synthesized_identity["visual"]
            existing_identity.emotion = synthesized_identity["emotion"]
            existing_identity.audience = synthesized_identity["audience"]
            existing_identity.keywords = synthesized_identity["keywords"]
            existing_identity.personality = synthesized_identity["personality"]
            existing_identity.design_rules = synthesized_identity["design_rules"]
            existing_identity.brand_summary = synthesized_identity["brand_summary"]
            existing_identity.confidence_score = synthesized_identity["confidence_score"]
            existing_identity.status = "ready"
            existing_identity.assets_processed_count = len(assets)
            await existing_identity.save()
            identity = existing_identity
        else:
            identity = BrandIdentity(
                brand_id=brand_id,
                version=1,
                voice=synthesized_identity["voice"],
                visual=synthesized_identity["visual"],
                emotion=synthesized_identity["emotion"],
                audience=synthesized_identity["audience"],
                keywords=synthesized_identity["keywords"],
                personality=synthesized_identity["personality"],
                design_rules=synthesized_identity["design_rules"],
                brand_summary=synthesized_identity["brand_summary"],
                confidence_score=synthesized_identity["confidence_score"],
                status="ready",
                assets_processed_count=len(assets)
            )
            await identity.insert()

        # Step 5: Save AI Memory
        memory = AIMemory(
            brand_id=brand_id,
            entity_type="identity",
            entity_id=str(identity.id),
            content_text=identity.brand_summary or f"{brand.name} Identity Model",
            summary=f"Living Brand Identity synthesized from {len(feature_records)} FeatureStore records for {brand.name}",
            metadata={"keywords": identity.keywords, "tone": identity.voice.get("tone")}
        )
        await memory.insert()

        # Step 6: Create Job Record
        job = Job(
            brand_id=brand_id,
            job_type="Identity",
            status="completed",
            progress=100,
            current_stage=f"Brand Identity Model Synthesized from {len(feature_records)} FeatureStore Records",
            result_reference={"identity_id": str(identity.id), "features_count": len(feature_records)}
        )
        await job.insert()

        return identity, job

    @classmethod
    @classmethod
    def _synthesize_from_feature_store(
        cls,
        brand_name: str,
        feature_records: List[FeatureStore],
        asset_count: int
    ) -> Dict[str, Any]:
        """
        Consensus Engine: Clusters feature_store records, resolves conflicts,
        votes by confidence scores, and calculates consensus.
        """
        if not feature_records:
            return {
                "voice": {"tone": None, "style": None, "confidence": 0.0},
                "visual": {"primary_colors": [], "secondary_colors": [], "logo_position": None, "layout": None, "typography": None},
                "emotion": {},
                "audience": {},
                "keywords": [],
                "personality": [],
                "design_rules": [],
                "brand_summary": f"No features extracted yet for {brand_name}.",
                "confidence_score": 0.0
            }

        voice_votes = Counter()
        tone_votes = Counter()
        color_votes = Counter()
        layout_votes = Counter()
        logo_pos_votes = Counter()
        style_votes = Counter()
        emotion_votes = Counter()
        personality_votes = Counter()
        keyword_votes = Counter()
        audience_votes = Counter()

        total_confidence = 0.0

        for r in feature_records:
            total_confidence += r.confidence
            val = r.value
            if not val:
                continue

            fname = r.feature_name
            if fname in ["brand_voice", "voice"] and isinstance(val, str):
                voice_votes[val] += r.confidence
            elif fname == "tone" and isinstance(val, str):
                tone_votes[val] += r.confidence
            elif fname in ["color_palette", "dominant_colors", "color_system"]:
                if isinstance(val, list):
                    for c in val:
                        color_votes[str(c)] += r.confidence
                elif isinstance(val, str):
                    color_votes[val] += r.confidence
            elif fname in ["layout", "visual_identity"] and isinstance(val, str):
                layout_votes[val] += r.confidence
            elif fname == "logo_position" and isinstance(val, str):
                logo_pos_votes[val] += r.confidence
            elif fname == "visual_style" and isinstance(val, str):
                style_votes[val] += r.confidence
            elif fname == "emotion":
                if isinstance(val, dict):
                    for k, v in val.items():
                        if isinstance(v, (int, float)):
                            emotion_votes[k] += v * (r.confidence / 100.0)
                elif isinstance(val, str):
                    emotion_votes[val] += r.confidence
            elif fname in ["brand_personality", "personality"]:
                if isinstance(val, list):
                    for p in val:
                        personality_votes[str(p)] += r.confidence
                elif isinstance(val, str):
                    personality_votes[str(p)] += r.confidence
            elif fname in ["keywords", "tagline", "headline"]:
                if isinstance(val, list):
                    for k in val:
                        keyword_votes[str(k)] += r.confidence
                elif isinstance(val, str):
                    keyword_votes[str(k)] += r.confidence
            elif fname == "audience":
                if isinstance(val, str):
                    audience_votes[val] += r.confidence
                elif isinstance(val, dict):
                    for k, v in val.items():
                        if isinstance(v, str):
                            audience_votes[f"{k}: {v}"] += r.confidence

        top_voice = voice_votes.most_common(1)[0][0] if voice_votes else None
        top_tone = tone_votes.most_common(1)[0][0] if tone_votes else None
        top_colors = [c[0] for c in color_votes.most_common(5)] if color_votes else []
        top_layout = layout_votes.most_common(1)[0][0] if layout_votes else None
        top_logo_pos = logo_pos_votes.most_common(1)[0][0] if logo_pos_votes else None
        top_style = style_votes.most_common(1)[0][0] if style_votes else None
        top_keywords = [k[0] for k in keyword_votes.most_common(5)] if keyword_votes else []
        top_personality = [p[0] for p in personality_votes.most_common(5)] if personality_votes else []
        top_audience = audience_votes.most_common(1)[0][0] if audience_votes else None

        avg_confidence = round((total_confidence / len(feature_records)) / 100.0, 2) if feature_records else 0.0

        emotions_dict = {}
        if emotion_votes:
            for k, v in emotion_votes.most_common(4):
                emotions_dict[k] = round(min(100.0, float(v)), 1)

        design_rules = []
        if top_colors:
            design_rules.append(f"Maintain primary brand color ({top_colors[0]}).")
        if top_logo_pos:
            design_rules.append(f"Position logo at {top_logo_pos}.")
        if top_style:
            design_rules.append(f"Adhere to visual style: {top_style}.")

        return {
            "voice": {
                "tone": top_tone or top_voice,
                "style": top_voice or top_style,
                "confidence": avg_confidence,
            },
            "visual": {
                "primary_colors": top_colors[:2],
                "secondary_colors": top_colors[2:],
                "logo_position": top_logo_pos,
                "layout": top_layout,
                "typography": top_style
            },
            "emotion": emotions_dict,
            "audience": {"primary": top_audience} if top_audience else {},
            "keywords": top_keywords,
            "personality": top_personality,
            "design_rules": design_rules,
            "brand_summary": f"{brand_name} Living Brand Identity synthesized from {len(feature_records)} FeatureStore evidence records across {asset_count} assets.",
            "confidence_score": avg_confidence
        }

    @staticmethod
    async def get_identity(brand_id: str, org_id: str) -> BrandIdentity:
        brand = await Brand.get(brand_id)
        if not brand or brand.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        identity = await BrandIdentity.find_one({"brand_id": brand_id})
        assets = await BrandAsset.find({"brand_id": brand_id}).to_list()
        if not identity:
            identity, _ = await IdentityService.build_identity(brand_id, org_id)
        elif len(assets) != identity.assets_processed_count or identity.status != "ready":
            identity, _ = await IdentityService.build_identity(brand_id, org_id, force_rebuild=True)

        return identity
