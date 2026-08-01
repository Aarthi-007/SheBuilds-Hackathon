from fastapi import APIRouter, Depends
from app.schemas.auth import StandardResponse
from app.schemas.trend import DiscoverTrendsRequest, GenerateTrendCampaignRequest, TrendReportDTO
from app.services.trend_service import TrendService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/trends", tags=["Module 6 - Brand Trend Intelligence Engine"])

@router.post("/discover", response_model=StandardResponse)
async def discover_trends(req: DiscoverTrendsRequest, current_user: User = Depends(get_current_user)):
    reports = await TrendService.discover_trends(req.brand_id, current_user.organization_id)
    dtos = [
        TrendReportDTO(
            id=str(r.id),
            brand_id=r.brand_id,
            trend=r.trend,
            category=r.category,
            alignment_score=r.alignment_score,
            trend_score=r.trend_score,
            competition_score=r.competition_score,
            forecast_score=r.forecast_score or 92.0,
            recommended_platform=r.recommended_platform,
            best_posting_time=r.best_posting_time,
            generated_campaign=r.generated_campaign,
            hashtags=r.hashtags,
            status=r.status
        )
        for r in reports
    ]
    return StandardResponse(
        success=True,
        message=f"Discovered {len(reports)} brand-aligned market trends",
        data=dtos
    )

@router.get("", response_model=StandardResponse)
async def get_trends(brand_id: str, current_user: User = Depends(get_current_user)):
    req = DiscoverTrendsRequest(brand_id=brand_id)
    return await discover_trends(req, current_user)

@router.post("/generate", response_model=StandardResponse)
async def generate_trend_campaign(req: GenerateTrendCampaignRequest, current_user: User = Depends(get_current_user)):
    campaign = await TrendService.generate_trend_campaign(req.brand_id, req.trend_name, current_user.organization_id, str(current_user.id))
    return StandardResponse(
        success=True,
        message="Trend-aligned campaign generated successfully",
        data={"campaign_id": str(campaign.id), "title": campaign.title, "platform": campaign.platform}
    )
