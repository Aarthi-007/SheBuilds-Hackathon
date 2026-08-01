import uuid
import json
from datetime import datetime
from pydantic import BaseModel

from agents.base_agent import BaseAgent
from services.claude_service import ClaudeService
from schemas.universal_content import UniversalContent
from schemas.brand_identity import BrandIdentityModel
from schemas.compliance_report import ComplianceReport


class ComplianceInput(BaseModel):
    content: UniversalContent
    brand_identity: BrandIdentityModel | None = None
    platform: str = "general"
    jurisdiction: str = "US"


class ComplianceAgent(BaseAgent):
    name = "compliance"

    def __init__(self):
        self._claude = ClaudeService()

    async def run(self, input_data: ComplianceInput) -> ComplianceReport:
        brand_guidelines = (
            json.dumps(input_data.brand_identity.model_dump())
            if input_data.brand_identity
            else "No brand guidelines provided."
        )

        variables = {
            "content_text": input_data.content.flattened_text[:3000],
            "platform": input_data.platform,
            "jurisdiction": input_data.jurisdiction,
            "brand_guidelines": brand_guidelines,
        }

        result = await self._claude.generate_structured(
            "compliance_check.md", variables, _ComplianceOutput
        )

        return ComplianceReport(
            report_id=str(uuid.uuid4()),
            content_id=input_data.content.content_id,
            passed=result.passed,
            violations=result.violations,
            notes=result.notes,
            created_at=datetime.utcnow(),
        )


class _ComplianceOutput(BaseModel):
    passed: bool
    violations: list[str]
    notes: str
