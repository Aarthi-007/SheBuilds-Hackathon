from database.mongo_client import get_db
from schemas.drift_report import DriftReport
from schemas.prediction_report import PredictionReport
from schemas.optimization_report import OptimizationReport
from schemas.compliance_report import ComplianceReport
from schemas.safety_report import SafetyReport
from schemas.copyright_report import CopyrightReport
from config.constants import (
    COL_DRIFT_REPORTS, COL_PREDICTION_REPORTS, COL_OPTIMIZATION_REPORTS,
    COL_COMPLIANCE_REPORTS, COL_SAFETY_REPORTS, COL_COPYRIGHT_REPORTS,
)


class ReportRepository:
    def __init__(self):
        db = get_db()
        self._drift = db[COL_DRIFT_REPORTS]
        self._prediction = db[COL_PREDICTION_REPORTS]
        self._optimization = db[COL_OPTIMIZATION_REPORTS]
        self._compliance = db[COL_COMPLIANCE_REPORTS]
        self._safety = db[COL_SAFETY_REPORTS]
        self._copyright = db[COL_COPYRIGHT_REPORTS]

    # --- save helpers ---
    async def save_drift(self, r: DriftReport) -> None:
        await self._drift.replace_one({"report_id": r.report_id}, r.model_dump(), upsert=True)

    async def save_prediction(self, r: PredictionReport) -> None:
        await self._prediction.replace_one({"report_id": r.report_id}, r.model_dump(), upsert=True)

    async def save_optimization(self, r: OptimizationReport) -> None:
        await self._optimization.replace_one({"report_id": r.report_id}, r.model_dump(), upsert=True)

    async def save_compliance(self, r: ComplianceReport) -> None:
        await self._compliance.replace_one({"report_id": r.report_id}, r.model_dump(), upsert=True)

    async def save_safety(self, r: SafetyReport) -> None:
        await self._safety.replace_one({"report_id": r.report_id}, r.model_dump(), upsert=True)

    async def save_copyright(self, r: CopyrightReport) -> None:
        await self._copyright.replace_one({"report_id": r.report_id}, r.model_dump(), upsert=True)

    # --- get by content_id ---
    async def get_drift(self, content_id: str) -> DriftReport | None:
        doc = await self._drift.find_one({"content_id": content_id})
        return DriftReport(**{k: v for k, v in doc.items() if k != "_id"}) if doc else None

    async def get_prediction(self, content_id: str) -> PredictionReport | None:
        doc = await self._prediction.find_one({"content_id": content_id})
        return PredictionReport(**{k: v for k, v in doc.items() if k != "_id"}) if doc else None

    async def get_optimization(self, content_id: str) -> OptimizationReport | None:
        doc = await self._optimization.find_one({"content_id": content_id})
        return OptimizationReport(**{k: v for k, v in doc.items() if k != "_id"}) if doc else None

    async def get_compliance(self, content_id: str) -> ComplianceReport | None:
        doc = await self._compliance.find_one({"content_id": content_id})
        return ComplianceReport(**{k: v for k, v in doc.items() if k != "_id"}) if doc else None

    async def get_safety(self, content_id: str) -> SafetyReport | None:
        doc = await self._safety.find_one({"content_id": content_id})
        return SafetyReport(**{k: v for k, v in doc.items() if k != "_id"}) if doc else None

    async def get_copyright(self, content_id: str) -> CopyrightReport | None:
        doc = await self._copyright.find_one({"content_id": content_id})
        return CopyrightReport(**{k: v for k, v in doc.items() if k != "_id"}) if doc else None
