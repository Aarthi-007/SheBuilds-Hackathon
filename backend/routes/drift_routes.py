from fastapi import APIRouter, HTTPException, Depends
from schemas.drift_report import DriftReport
from schemas.api_models import IngestContentRequest
from repositories.report_repository import ReportRepository

router = APIRouter(prefix="/drift", tags=["drift"])


def _repo():
    return ReportRepository()


@router.get("/{content_id}", response_model=DriftReport)
async def get_drift(content_id: str, repo: ReportRepository = Depends(_repo)):
    report = await repo.get_drift(content_id)
    if not report:
        raise HTTPException(status_code=404, detail="Drift report not found")
    return report


@router.post("/check", response_model=DriftReport)
async def check_drift(request: IngestContentRequest):
    from dependencies import get_orchestrator
    from orchestrator.orchestrator_agent import OrchestratorRequest
    from config.constants import WORKFLOW_QUICK_DRIFT

    orchestrator = get_orchestrator()
    orch_request = OrchestratorRequest(
        workflow=WORKFLOW_QUICK_DRIFT,
        inputs={
            "company_id": request.company_id,
            "modality": request.modality,
            "payload": request.payload,
        },
    )
    result = await orchestrator.run(orch_request)
    drift_data = result.results.get("drift")
    if not drift_data:
        raise HTTPException(status_code=500, detail="Drift check failed")
    return DriftReport(**drift_data)
