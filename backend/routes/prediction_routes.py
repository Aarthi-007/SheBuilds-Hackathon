from fastapi import APIRouter, HTTPException
from schemas.prediction_report import PredictionReport
from schemas.api_models import IngestContentRequest

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("", response_model=PredictionReport)
async def predict(request: IngestContentRequest):
    from dependencies import get_orchestrator
    from orchestrator.orchestrator_agent import OrchestratorRequest
    from config.constants import WORKFLOW_FULL_INGEST

    orchestrator = get_orchestrator()
    orch_request = OrchestratorRequest(
        workflow=WORKFLOW_FULL_INGEST,
        inputs={
            "company_id": request.company_id,
            "modality": request.modality,
            "payload": request.payload,
        },
    )
    result = await orchestrator.run(orch_request)
    prediction_data = result.results.get("prediction")
    if not prediction_data:
        raise HTTPException(status_code=500, detail="Prediction failed")
    return PredictionReport(**prediction_data)
