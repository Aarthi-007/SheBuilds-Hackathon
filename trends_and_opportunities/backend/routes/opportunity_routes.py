from fastapi import APIRouter

from schemas.opportunity_report import TrackOpportunitiesRequest, TrackOpportunitiesResult
from repositories.opportunity_repository import OpportunityRepository

router = APIRouter(prefix="/api/v1/opportunities", tags=["opportunities"])


@router.post("/scan", response_model=TrackOpportunitiesResult)
async def scan_opportunities(request: TrackOpportunitiesRequest):
    """On-demand trigger — delegates to the shared agent instance built in main.py."""
    from main import shared_agent
    return await shared_agent.run(request)


@router.get("/{company_id}")
async def list_opportunities(company_id: str, only_opportunities: bool = True):
    """List past opportunity reports, enriched with signal headline/source/url."""
    repo = OpportunityRepository()
    return await repo.list_reports_enriched(company_id, only_opportunities=only_opportunities)
