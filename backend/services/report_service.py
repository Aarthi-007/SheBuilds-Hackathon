from typing import Optional, Dict, Any
from repositories.report_repository import ReportRepository
from schemas.drift_report import DriftReport
from schemas.prediction_report import PredictionReport
from schemas.optimization_report import OptimizationReport
from schemas.compliance_report import ComplianceReport
from schemas.safety_report import SafetyReport
from schemas.copyright_report import CopyrightReport


class ReportService:
    def __init__(self):
        self._repo = ReportRepository()

    async def persist_all(
        self,
        drift: Optional[DriftReport] = None,
        prediction: Optional[PredictionReport] = None,
        optimization: Optional[OptimizationReport] = None,
        compliance: Optional[ComplianceReport] = None,
        safety: Optional[SafetyReport] = None,
        copyright: Optional[CopyrightReport] = None,
    ) -> None:
        if drift:
            await self._repo.save_drift(drift)
        if prediction:
            await self._repo.save_prediction(prediction)
        if optimization:
            await self._repo.save_optimization(optimization)
        if compliance:
            await self._repo.save_compliance(compliance)
        if safety:
            await self._repo.save_safety(safety)
        if copyright:
            await self._repo.save_copyright(copyright)

    async def get_all_for_content(self, content_id: str) -> Dict[str, Any]:
        return {
            "drift": await self._repo.get_drift(content_id),
            "prediction": await self._repo.get_prediction(content_id),
            "optimization": await self._repo.get_optimization(content_id),
            "compliance": await self._repo.get_compliance(content_id),
            "safety": await self._repo.get_safety(content_id),
            "copyright": await self._repo.get_copyright(content_id),
        }
