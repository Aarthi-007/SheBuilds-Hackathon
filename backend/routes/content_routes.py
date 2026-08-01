from fastapi import APIRouter, HTTPException, Depends
from schemas.api_models import IngestContentRequest, IngestContentResponse
from schemas.universal_content import UniversalContent
from repositories.content_repository import ContentRepository
from repositories.report_repository import ReportRepository

router = APIRouter(prefix="/content", tags=["content"])


def _get_content_repo():
    return ContentRepository()


def _get_report_repo():
    return ReportRepository()


@router.post("/ingest", response_model=IngestContentResponse)
async def ingest_content(
    request: IngestContentRequest,
    content_repo: ContentRepository = Depends(_get_content_repo),
    report_repo: ReportRepository = Depends(_get_report_repo),
):
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
    results = result.results

    content: UniversalContent = _dict_to(UniversalContent, results.get("perception"))
    await content_repo.save(content)

    drift = _dict_to_optional("drift_report", results, report_repo)
    prediction = _dict_to_optional("prediction_report", results, report_repo)
    optimization = _dict_to_optional("optimization_report", results, report_repo)
    compliance = _dict_to_optional("compliance_report", results, report_repo)
    safety = _dict_to_optional("safety_report", results, report_repo)
    copyright_ = _dict_to_optional("copyright_report", results, report_repo)

    from schemas.drift_report import DriftReport
    from schemas.prediction_report import PredictionReport
    from schemas.optimization_report import OptimizationReport
    from schemas.compliance_report import ComplianceReport
    from schemas.safety_report import SafetyReport
    from schemas.copyright_report import CopyrightReport

    schema_map = {
        "drift": DriftReport, "prediction": PredictionReport,
        "optimization": OptimizationReport, "compliance": ComplianceReport,
        "safety": SafetyReport, "copyright": CopyrightReport,
    }

    def get_report(key, schema):
        data = results.get(key)
        return schema(**data) if data else None

    return IngestContentResponse(
        content_id=content.content_id,
        universal_content=content,
        drift_report=get_report("drift", DriftReport),
        prediction_report=get_report("prediction", PredictionReport),
        optimization_report=get_report("optimization", OptimizationReport),
        compliance_report=get_report("compliance", ComplianceReport),
        safety_report=get_report("safety", SafetyReport),
        copyright_report=get_report("copyright", CopyrightReport),
    )


@router.get("/{content_id}", response_model=UniversalContent)
async def get_content(
    content_id: str,
    repo: ContentRepository = Depends(_get_content_repo),
):
    content = await repo.get_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


def _dict_to(schema, data):
    if data is None:
        return None
    if isinstance(data, dict):
        return schema(**data)
    return data


def _dict_to_optional(key, results, repo):
    return results.get(key)
