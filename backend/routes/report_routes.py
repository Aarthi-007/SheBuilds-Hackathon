from fastapi import APIRouter, HTTPException, Depends
from schemas.api_models import IngestContentResponse
from schemas.universal_content import UniversalContent
from repositories.content_repository import ContentRepository
from repositories.report_repository import ReportRepository

router = APIRouter(prefix="/reports", tags=["reports"])


def _content_repo():
    return ContentRepository()


def _report_repo():
    return ReportRepository()


@router.get("/{content_id}", response_model=IngestContentResponse)
async def get_all_reports(
    content_id: str,
    content_repo: ContentRepository = Depends(_content_repo),
    report_repo: ReportRepository = Depends(_report_repo),
):
    content = await content_repo.get_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return IngestContentResponse(
        content_id=content_id,
        universal_content=content,
        drift_report=await report_repo.get_drift(content_id),
        prediction_report=await report_repo.get_prediction(content_id),
        optimization_report=await report_repo.get_optimization(content_id),
        compliance_report=await report_repo.get_compliance(content_id),
        safety_report=await report_repo.get_safety(content_id),
        copyright_report=await report_repo.get_copyright(content_id),
    )
