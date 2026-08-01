import uuid
from datetime import datetime
from pydantic import BaseModel

from agents.base_agent import BaseAgent
from services.claude_service import ClaudeService
from schemas.universal_content import UniversalContent
from schemas.safety_report import SafetyReport


class SafetyInput(BaseModel):
    content: UniversalContent


class SafetyAgent(BaseAgent):
    name = "safety"

    def __init__(self):
        self._claude = ClaudeService()

    async def run(self, input_data: SafetyInput) -> SafetyReport:
        variables = {"content_text": input_data.content.flattened_text[:3000]}

        result = await self._claude.generate_structured(
            "safety_check.md", variables, _SafetyOutput
        )

        return SafetyReport(
            report_id=str(uuid.uuid4()),
            content_id=input_data.content.content_id,
            toxicity_flag=result.toxicity_flag,
            bias_flag=result.bias_flag,
            misinformation_flag=result.misinformation_flag,
            notes=result.notes,
            created_at=datetime.utcnow(),
        )


class _SafetyOutput(BaseModel):
    toxicity_flag: bool
    bias_flag: bool
    misinformation_flag: bool
    notes: str
