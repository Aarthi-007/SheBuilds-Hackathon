from fastapi import APIRouter, HTTPException
from schemas.optimization_report import OptimizationReport
from schemas.api_models import IngestContentRequest

router = APIRouter(prefix="/optimize", tags=["optimization"])


@router.post("", response_model=OptimizationReport)
async def optimize(request: IngestContentRequest):
    from dependencies import get_orchestrator
    from orchestrator.orchestrator_agent import OrchestratorRequest
    from config.constants import WORKFLOW_OPTIMIZE_ONLY

    orchestrator = get_orchestrator()
    orch_request = OrchestratorRequest(
        workflow=WORKFLOW_OPTIMIZE_ONLY,
        inputs={
            "company_id": request.company_id,
            "modality": request.modality,
            "payload": request.payload,
        },
    )
    result = await orchestrator.run(orch_request)
    opt_data = result.results.get("optimization")
    if not opt_data:
        raise HTTPException(status_code=500, detail="Optimization failed")
    return OptimizationReport(**opt_data)
