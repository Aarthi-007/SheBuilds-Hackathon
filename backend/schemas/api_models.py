from pydantic import BaseModel
from typing import Literal
from .universal_content import UniversalContent
from .drift_report import DriftReport
from .prediction_report import PredictionReport
from .optimization_report import OptimizationReport
from .compliance_report import ComplianceReport
from .safety_report import SafetyReport
from .copyright_report import CopyrightReport


class IngestContentRequest(BaseModel):
    company_id: str
    modality: Literal["text", "image", "video"]
    payload: str  # raw text or base64/URL depending on modality


class IngestContentResponse(BaseModel):
    content_id: str
    universal_content: UniversalContent
    drift_report: DriftReport | None = None
    prediction_report: PredictionReport | None = None
    optimization_report: OptimizationReport | None = None
    compliance_report: ComplianceReport | None = None
    safety_report: SafetyReport | None = None
    copyright_report: CopyrightReport | None = None
