from fastapi import APIRouter, HTTPException, Depends
from schemas.brand_identity import BrandIdentityModel
from repositories.brand_repository import BrandRepository

router = APIRouter(prefix="/brand", tags=["brand"])


def _repo():
    return BrandRepository()


@router.get("/{company_id}", response_model=BrandIdentityModel)
async def get_brand(company_id: str, repo: BrandRepository = Depends(_repo)):
    model = await repo.get_by_company(company_id)
    if not model:
        raise HTTPException(status_code=404, detail="Brand identity not found")
    return model


@router.post("/{company_id}/relearn", response_model=BrandIdentityModel)
async def relearn_brand(company_id: str, repo: BrandRepository = Depends(_repo)):
    from dependencies import get_orchestrator
    from orchestrator.orchestrator_agent import OrchestratorRequest
    from config.constants import WORKFLOW_COMPETITOR_SCAN
    from repositories.content_repository import ContentRepository

    content_repo = ContentRepository()
    contents = await content_repo.list_by_company(company_id)
    if not contents:
        raise HTTPException(status_code=400, detail="No content found for company")

    orchestrator = get_orchestrator()
    orch_request = OrchestratorRequest(
        workflow=WORKFLOW_COMPETITOR_SCAN,
        inputs={"company_id": company_id, "content_batch": [c.model_dump() for c in contents]},
    )
    result = await orchestrator.run(orch_request)
    model_data = result.results.get("brand_identity")
    if not model_data:
        raise HTTPException(status_code=500, detail="Brand relearn failed")
    return BrandIdentityModel(**model_data)
