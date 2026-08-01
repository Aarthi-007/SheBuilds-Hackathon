from fastapi import APIRouter, HTTPException, Depends
from schemas.compliance_report import ComplianceReport
from repositories.report_repository import ReportRepository

router = APIRouter(prefix="/compliance", tags=["compliance"])


def _repo():
    return ReportRepository()


@router.get("/{content_id}", response_model=ComplianceReport)
async def get_compliance(content_id: str, repo: ReportRepository = Depends(_repo)):
    report = await repo.get_compliance(content_id)
    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")
    return report
