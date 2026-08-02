"""
Schemas for Impact Simulation.

Impact Simulation takes a piece of AI-generated content and asks Claude to
research (web search) and reason about how that content will perform / age
over time, then returns one structured report.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ImpactSimulationRequest(BaseModel):
    company_id: str = Field(..., description="Tenant/company the content belongs to")
    modality: Literal["text", "image"] = Field(
        "text", description="What kind of content is being simulated"
    )
    content: str | None = Field(
        None,
        description="Required for modality='text'. For image, an optional caption "
        "or accompanying copy that goes alongside the media.",
    )
    media: list[str] | None = Field(
        None,
        description="Required for modality='image'. One base64 data URL, "
        "e.g. 'data:image/jpeg;base64,...'.",
    )
    content_type: Literal["blog", "ad", "social_post", "email", "video_script", "other"] = "other"
    horizon: Literal["30d", "90d", "1y"] = Field(
        "90d", description="How far into the future the simulation should reason about"
    )
    extra_context: str | None = Field(
        None, description="Optional context: campaign goal, audience, industry notes"
    )

    def validate_payload(self) -> None:
        if self.modality == "text" and not (self.content and self.content.strip()):
            raise ValueError("content is required when modality is 'text'")
        if self.modality == "image" and not self.media:
            raise ValueError("media is required when modality is 'image'")


class TrendSignal(BaseModel):
    trend: str
    relevance: Literal["supports", "neutral", "works_against"]
    explanation: str
    source_url: str | None = None


class RiskOrOpportunity(BaseModel):
    label: str
    severity: Literal["low", "medium", "high"]
    explanation: str


class PredictedTrajectory(BaseModel):
    outlook: Literal["improving", "stable", "declining", "volatile"]
    confidence_score: float = Field(..., ge=0, le=1)
    reasoning: str


class ImpactSimulationReport(BaseModel):
    report_id: str
    content_id: str | None = None
    company_id: str
    modality: Literal["text", "image"] = "text"
    perceived_description: str | None = Field(
        None, description="For image: what Gemini's perception step saw, before Claude reasoned about it"
    )
    horizon: str
    summary: str
    predicted_trajectory: PredictedTrajectory
    trend_signals: list[TrendSignal]
    risks: list[RiskOrOpportunity]
    opportunities: list[RiskOrOpportunity]
    recommendations: list[str]
    citations: list[str] = Field(default_factory=list)
    created_at: datetime
