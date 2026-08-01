from typing import List
from fastapi import HTTPException, status
from app.models.brand import Brand
from app.models.trend import TrendReport
from app.models.campaign import Campaign, CampaignVersion
from app.services.identity_service import IdentityService
from app.ai.multimodal_analyzer import MultimodalAnalyzer

class TrendService:
    @staticmethod
    async def discover_trends(brand_id: str, org_id: str) -> List[TrendReport]:
        brand = await Brand.get(brand_id)
        if not brand or brand.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        identity = await IdentityService.get_identity(brand_id, org_id)
        identity_dict = {"voice": identity.voice, "audience": identity.audience}

        trends_data = MultimodalAnalyzer.discover_and_align_trends(brand.name, identity_dict)
        
        reports = []
        for t in trends_data:
            existing = await TrendReport.find_one({"brand_id": brand_id, "trend": t["trend"]})
            if not existing:
                report = TrendReport(
                    brand_id=brand_id,
                    trend=t["trend"],
                    category=t["category"],
                    alignment_score=t["alignment_score"],
                    trend_score=t["trend_score"],
                    competition_score=t["competition_score"],
                    forecast_score=t.get("forecast_score", 92.0),
                    recommended_platform=t["recommended_platform"],
                    best_posting_time=t["best_posting_time"],
                    generated_campaign=t["generated_campaign"],
                    hashtags=t["hashtags"],
                    status="recommended"
                )
                await report.insert()
                reports.append(report)
            else:
                reports.append(existing)
                
        return reports

    @staticmethod
    async def generate_trend_campaign(brand_id: str, trend_name: str, org_id: str, user_id: str) -> Campaign:
        brand = await Brand.get(brand_id)
        if not brand or brand.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        trend_report = await TrendReport.find_one({"brand_id": brand_id, "trend": trend_name})
        if not trend_report:
            trends = await TrendService.discover_trends(brand_id, org_id)
            trend_report = trends[0]

        campaign_title = trend_report.generated_campaign.get("title", f"{trend_name} Campaign")
        caption = trend_report.generated_campaign.get("caption", "Brand campaign generated from trend.")

        campaign = Campaign(
            brand_id=brand_id,
            title=campaign_title,
            description=f"Generated from market trend: {trend_name}",
            platform=trend_report.recommended_platform,
            objective="Trend Awareness",
            status="certified",
            current_version=1,
            created_by=user_id
        )
        await campaign.insert()

        version = CampaignVersion(
            campaign_id=str(campaign.id),
            version=1,
            text_content=caption,
            generated_by="Brand Trend Intelligence Engine",
            validation_score=trend_report.alignment_score,
            approved=True
        )
        await version.insert()

        return campaign
