from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status
from app.models.brand import Brand, BrandAsset
from app.models.identity import BrandIdentity, AIMemory
from app.models.job import Job
from app.ai.multimodal_analyzer import MultimodalAnalyzer

class IdentityService:
    @staticmethod
    async def build_identity(brand_id: str, org_id: str, force_rebuild: bool = False, groq_api_key: Optional[str] = None) -> Tuple[BrandIdentity, Job]:
        brand = await Brand.get(brand_id)
        if not brand or brand.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        existing_identity = await BrandIdentity.find_one({"brand_id": brand_id})
        assets = await BrandAsset.find({"brand_id": brand_id}).to_list()
        asset_dicts = [
            {
                "asset_type": a.asset_type,
                "mime_type": a.mime_type,
                "storage_path": a.storage_path,
                "metadata": a.metadata
            }
            for a in assets
        ]
        
        analysis_result = MultimodalAnalyzer.build_brand_identity(brand.name, asset_dicts, groq_api_key=groq_api_key)
        
        if existing_identity:
            existing_identity.version += 1
            existing_identity.voice = analysis_result["voice"]
            existing_identity.visual = analysis_result["visual"]
            existing_identity.emotion = analysis_result["emotion"]
            existing_identity.audience = analysis_result["audience"]
            existing_identity.keywords = analysis_result["keywords"]
            existing_identity.personality = analysis_result["personality"]
            existing_identity.design_rules = analysis_result["design_rules"]
            existing_identity.brand_summary = analysis_result["brand_summary"]
            existing_identity.status = "ready"
            existing_identity.assets_processed_count = len(assets)
            await existing_identity.save()
            identity = existing_identity
        else:
            identity = BrandIdentity(
                brand_id=brand_id,
                version=1,
                voice=analysis_result["voice"],
                visual=analysis_result["visual"],
                emotion=analysis_result["emotion"],
                audience=analysis_result["audience"],
                keywords=analysis_result["keywords"],
                personality=analysis_result["personality"],
                design_rules=analysis_result["design_rules"],
                brand_summary=analysis_result["brand_summary"],
                confidence_score=analysis_result.get("confidence_score", 0.95),
                status="ready",
                assets_processed_count=len(assets)
            )
            await identity.insert()

        for a in assets:
            a.processing_status = "completed"
            await a.save()

        memory = AIMemory(
            brand_id=brand_id,
            entity_type="identity",
            entity_id=str(identity.id),
            content_text=identity.brand_summary or f"{brand.name} Identity Model",
            summary=f"Brand identity model for {brand.name}",
            metadata={"keywords": identity.keywords, "tone": identity.voice.get("tone")}
        )
        await memory.insert()

        job = Job(
            brand_id=brand_id,
            job_type="Identity",
            status="completed",
            progress=100,
            current_stage="Brand Identity Model Ready (Groq AI Processing Completed)" if (groq_api_key or analysis_result.get("groq_raw_intelligence")) else "Brand Identity Model Ready",
            result_reference={"identity_id": str(identity.id)}
        )
        await job.insert()

        return identity, job

    @staticmethod
    async def get_identity(brand_id: str, org_id: str) -> BrandIdentity:
        brand = await Brand.get(brand_id)
        if not brand or brand.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        identity = await BrandIdentity.find_one({"brand_id": brand_id})
        if not identity:
            identity, _ = await IdentityService.build_identity(brand_id, org_id)
            
        return identity
