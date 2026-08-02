"""
OpportunityAgent — the "Trends & Opportunities" layer.

Flow:
  1. Fetch recent news via News API for the company's industry keywords.
  2. Skip articles already seen (deduplication by URL hash in trend_signals).
  3. Embed each new signal and similarity-search against brand knowledge + campaigns in Pinecone.
  4. Signals above similarity_threshold are sent to Claude for judgment.
  5. If Claude marks it as an opportunity, fire a notification via NotificationService.
"""

import uuid
import hashlib
from datetime import datetime

from agents.base_agent import BaseAgent
from schemas.trend_knowledge import TrendSignal, TrendMatch
from schemas.opportunity_report import (
    TrackOpportunitiesRequest,
    TrackOpportunitiesResult,
    OpportunityReport,
)
from services.news_service import NewsService
from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService
from services.claude_service import ClaudeService
from services.notification_service import NotificationService
from repositories.opportunity_repository import OpportunityRepository
from repositories.brand_repository import BrandRepository
from config.constants import PINECONE_INDEX_BRAND, PINECONE_INDEX_CAMPAIGN


class OpportunityAgent(BaseAgent):
    name = "opportunity_agent"

    def __init__(
        self,
        news_service: NewsService,
        embedding_service: EmbeddingService,
        pinecone_service: PineconeService,
        claude_service: ClaudeService,
        notification_service: NotificationService,
        opportunity_repository: OpportunityRepository,
        brand_repository: BrandRepository,
    ):
        self._news = news_service
        self._embed = embedding_service
        self._pinecone = pinecone_service
        self._claude = claude_service
        self._notify = notification_service
        self._opportunity_repo = opportunity_repository
        self._brand_repo = brand_repository

    async def run(self, input_data: TrackOpportunitiesRequest) -> TrackOpportunitiesResult:
        raw_articles = await self._news.fetch_trending(
            query=" OR ".join(input_data.industry_keywords)
        )

        # Deduplicate: skip URLs we've already processed for this company
        seen_urls = await self._opportunity_repo.get_seen_urls(input_data.company_id)
        new_articles = [a for a in raw_articles if a["url"] not in seen_urls]

        signals = self._articles_to_signals(input_data.company_id, new_articles)

        matches: list[TrendMatch] = []
        for signal in signals:
            await self._opportunity_repo.save_signal(signal)
            match = await self._find_similar(signal, input_data.similarity_threshold)
            if match:
                matches.append(match)

        reports: list[OpportunityReport] = []
        for match in matches:
            report = await self._evaluate_opportunity(match)
            await self._opportunity_repo.save_report(report)
            if report.is_opportunity:
                await self._notify.notify(report, headline=match.signal.headline)
            reports.append(report)

        return TrackOpportunitiesResult(
            company_id=input_data.company_id,
            signals_fetched=len(new_articles),
            matches_found=len(matches),
            opportunity_reports=reports,
        )

    # ── private helpers ────────────────────────────────────────────────────

    def _articles_to_signals(self, company_id: str, articles: list[dict]) -> list[TrendSignal]:
        signals = []
        for article in articles:
            flattened = f"{article['headline']}. {article['summary']}"
            signals.append(
                TrendSignal(
                    signal_id=hashlib.md5(article["url"].encode()).hexdigest(),
                    company_id=company_id,
                    headline=article["headline"],
                    summary=article["summary"],
                    source=article["source"],
                    url=article["url"],
                    published_at=article["published_at"],
                    flattened_text=flattened,
                )
            )
        return signals

    async def _find_similar(self, signal: TrendSignal, threshold: float) -> TrendMatch | None:
        vector = self._embed.embed(signal.flattened_text)

        brand_matches = await self._pinecone.query(
            index=PINECONE_INDEX_BRAND, namespace=signal.company_id, vector=vector, top_k=1
        )
        campaign_matches = await self._pinecone.query(
            index=PINECONE_INDEX_CAMPAIGN, namespace=signal.company_id, vector=vector, top_k=1
        )

        best = None
        for matched_against, results in (
            ("brand_identity", brand_matches),
            ("campaign", campaign_matches),
        ):
            if results and results[0]["score"] >= threshold:
                candidate = TrendMatch(
                    signal=signal,
                    similarity_score=results[0]["score"],
                    matched_against=matched_against,
                    matched_id=results[0]["id"],
                )
                if best is None or candidate.similarity_score > best.similarity_score:
                    best = candidate
        return best

    async def _evaluate_opportunity(self, match: TrendMatch) -> OpportunityReport:
        """Claude judges the trend against the brand knowledge base and recommends campaigns."""
        brand_identity = await self._brand_repo.get(match.signal.company_id)

        report = await self._claude.generate_structured(
            prompt_file="opportunity_evaluation.md",
            variables={
                "brand_identity_json": brand_identity.model_dump_json() if brand_identity else "{}",
                "headline": match.signal.headline,
                "summary": match.signal.summary,
                "source": match.signal.source,
                "published_at": match.signal.published_at.isoformat(),
                "matched_against": match.matched_against,
                "similarity_score": match.similarity_score,
                "company_id": match.signal.company_id,
                "signal_id": match.signal.signal_id,
            },
            schema=OpportunityReport,
        )
        report.created_at = datetime.utcnow()
        return report
