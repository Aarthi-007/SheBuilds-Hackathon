from typing import Optional
from fastapi import HTTPException, status
from app.models.brand import Brand
from app.models.validation import ValidationReport
from app.schemas.validation import ValidationCheckRequest
from app.services.identity_service import IdentityService
from app.ai.multimodal_analyzer import MultimodalAnalyzer

class ValidationService:
    @staticmethod
    async def validate_content(org_id: str, req: ValidationCheckRequest) -> ValidationReport:
        brand = await Brand.get(req.brand_id)
        if not brand or brand.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        identity = await IdentityService.get_identity(req.brand_id, org_id)
        identity_dict = {
            "voice": identity.voice,
            "visual": identity.visual,
            "keywords": identity.keywords,
            "design_rules": identity.design_rules
        }

        eval_result = MultimodalAnalyzer.validate_content(
            identity_dict,
            req.text_content,
            image_url=req.image_url,
            platform=req.platform
        )

        campaign_id = req.campaign_id or "adhoc_campaign"
        campaign_version_id = "v1"

        report = ValidationReport(
            campaign_id=campaign_id,
            campaign_version_id=campaign_version_id,
            brand_id=req.brand_id,
            overall_score=eval_result["overall_score"],
            status=eval_result["status"],
            scores=eval_result["scores"],
            issues=eval_result["issues"],
            recommendations=eval_result["recommendations"]
        )
        await report.insert()
        return report

    @staticmethod
    async def get_report_by_campaign(campaign_id: str) -> ValidationReport:
        report = await ValidationReport.find_one({"campaign_id": campaign_id})
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation report not found")
        return report
