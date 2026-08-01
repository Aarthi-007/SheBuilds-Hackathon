from fastapi import APIRouter, HTTPException, Depends
from schemas.competitor_profile import CompetitorProfile
from repositories.competitor_repository import CompetitorRepository

router = APIRouter(prefix="/competitors", tags=["competitors"])


def _repo():
    return CompetitorRepository()


@router.get("/{company_id}", response_model=list[CompetitorProfile])
async def list_competitors(company_id: str, repo: CompetitorRepository = Depends(_repo)):
    return await repo.list_by_company(company_id)


@router.post("/{company_id}/scan", response_model=list[CompetitorProfile])
async def scan_competitors(company_id: str, repo: CompetitorRepository = Depends(_repo)):
    from dependencies import get_orchestrator
    from orchestrator.orchestrator_agent import OrchestratorRequest
    from config.constants import WORKFLOW_COMPETITOR_SCAN
    from repositories.brand_repository import BrandRepository

    brand_repo = BrandRepository()
    brand = await brand_repo.get_by_company(company_id)
    if not brand:
        raise HTTPException(status_code=400, detail="Brand identity not found — ingest content first")

    orchestrator = get_orchestrator()
    orch_request = OrchestratorRequest(
        workflow=WORKFLOW_COMPETITOR_SCAN,
        inputs={"company_id": company_id, "brand_identity": brand.model_dump()},
    )
    await orchestrator.run(orch_request)
    return await repo.list_by_company(company_id)
