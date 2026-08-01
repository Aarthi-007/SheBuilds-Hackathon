from fastapi import APIRouter, Depends
from app.schemas.auth import StandardResponse
from app.schemas.dashboard import DashboardSummaryDTO
from app.services.dashboard_service import DashboardService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="", tags=["Module 9 - Dashboard & Analytics"])

@router.get("/dashboard", response_model=StandardResponse)
async def get_dashboard(current_user: User = Depends(get_current_user)):
    summary = await DashboardService.get_dashboard_summary(current_user.organization_id)
    dto = DashboardSummaryDTO(
        total_brands=summary["total_brands"],
        total_campaigns=summary["total_campaigns"],
        avg_certification_score=summary["avg_certification_score"],
        active_trends_count=summary["active_trends_count"],
        metrics=summary["metrics"],
        recent_activities=summary["recent_activities"],
        recent_campaigns=summary["recent_campaigns"],
        top_aligned_trends=summary["top_aligned_trends"]
    )
    return StandardResponse(success=True, data=dto)

@router.get("/analytics", response_model=StandardResponse)
async def get_analytics(current_user: User = Depends(get_current_user)):
    summary = await DashboardService.get_dashboard_summary(current_user.organization_id)
    return StandardResponse(success=True, data=summary)
