import uuid
import json
from datetime import datetime
from pydantic import BaseModel

from agents.base_agent import BaseAgent
from services.claude_service import ClaudeService
from services.tavily_service import TavilyService
from schemas.universal_content import UniversalContent
from schemas.copyright_report import CopyrightReport


class CopyrightInput(BaseModel):
    content: UniversalContent


class CopyrightAgent(BaseAgent):
    name = "copyright"

    def __init__(self):
        self._claude = ClaudeService()
        self._tavily = TavilyService()

    async def run(self, input_data: CopyrightInput) -> CopyrightReport:
        content_text = input_data.content.flattened_text[:500]

        # Search for similar content externally
        search_results = self._tavily.search(
            f'"{content_text[:100]}"', max_results=5
        )

        variables = {
            "content_text": input_data.content.flattened_text[:3000],
            "search_results": json.dumps(
                [{"title": r.get("title"), "url": r.get("url"), "content": r.get("content", "")[:200]} for r in search_results],
                indent=2,
            ),
        }

        result = await self._claude.generate_structured(
            "copyright_check.md", variables, _CopyrightOutput
        )

        return CopyrightReport(
            report_id=str(uuid.uuid4()),
            content_id=input_data.content.content_id,
            plagiarism_flag=result.plagiarism_flag,
            trademark_conflicts=result.trademark_conflicts,
            sources_matched=result.sources_matched,
            notes=result.notes,
            created_at=datetime.utcnow(),
        )


class _CopyrightOutput(BaseModel):
    plagiarism_flag: bool
    trademark_conflicts: list[str]
    sources_matched: list[str]
    notes: str
