from __future__ import annotations

import uuid
from datetime import datetime, timezone

from backend.agents.base_agent import BaseAgent
from backend.schemas.impact_simulation import (
    ImpactSimulationReport,
    ImpactSimulationRequest,
    PredictedTrajectory,
    RiskOrOpportunity,
    TrendSignal,
)
from backend.services.claude_service import ClaudeService
from backend.services.gemini_service import GeminiService


class ImpactSimulationAgent(BaseAgent):
    """
    Given AI-generated content (text or image), researches relevant trends
    and reasons about how the content will fare in the future, then produces
    a comprehensive analysis report.

    Images go through GeminiService (perception) first to produce a text
    description; everything downstream works off text only.
    """

    name = "impact_simulation_agent"

    def __init__(
        self,
        claude_service: ClaudeService | None = None,
        gemini_service: GeminiService | None = None,
    ) -> None:
        self._claude = claude_service or ClaudeService()
        self._gemini = gemini_service or GeminiService()

    async def run(self, input_data: ImpactSimulationRequest) -> ImpactSimulationReport:
        input_data.validate_payload()

        perceived_description: str | None = None
        flattened_content: str

        if input_data.modality == "text":
            flattened_content = input_data.content  # type: ignore[assignment]
        else:
            # modality == "image": run Gemini perception first
            perception = await self._gemini.perceive(
                media_data_urls=input_data.media or [],
                caption=input_data.content,
            )
            perceived_description = perception.get("description", "")
            parts = [perceived_description]
            if perception.get("on_screen_text"):
                parts.append(f"On-screen text: {perception['on_screen_text']}")
            if perception.get("visual_style"):
                parts.append(f"Visual style: {perception['visual_style']}")
            if input_data.content:
                parts.append(f"Caption/copy provided: {input_data.content}")
            flattened_content = "\n".join(p for p in parts if p)

        raw = await self._claude.research_and_reason(
            prompt_name="impact_simulation.md",
            variables={
                "content": flattened_content,
                "content_type": input_data.content_type,
                "horizon": input_data.horizon,
                "company_id": input_data.company_id,
                "extra_context": input_data.extra_context or "none provided",
            },
        )

        return ImpactSimulationReport(
            report_id=str(uuid.uuid4()),
            content_id=None,
            company_id=input_data.company_id,
            modality=input_data.modality,
            perceived_description=perceived_description,
            horizon=input_data.horizon,
            summary=raw["summary"],
            predicted_trajectory=PredictedTrajectory(**raw["predicted_trajectory"]),
            trend_signals=[TrendSignal(**t) for t in raw.get("trend_signals", [])],
            risks=[RiskOrOpportunity(**r) for r in raw.get("risks", [])],
            opportunities=[RiskOrOpportunity(**o) for o in raw.get("opportunities", [])],
            recommendations=raw.get("recommendations", []),
            citations=raw.get("citations", []),
            created_at=datetime.now(timezone.utc),
        )
