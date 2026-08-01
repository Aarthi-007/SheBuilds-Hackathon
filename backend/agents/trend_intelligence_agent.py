import uuid
import json
from datetime import datetime
from pydantic import BaseModel

from agents.base_agent import BaseAgent
from services.claude_service import ClaudeService
from services.tavily_service import TavilyService
from services.scraper_service import ScraperService
from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService
from repositories.competitor_repository import CompetitorRepository
from repositories.trend_repository import TrendRepository
from schemas.brand_identity import BrandIdentityModel
from schemas.trend_knowledge import TrendKnowledge
from schemas.competitor_profile import CompetitorProfile
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class TrendInput(BaseModel):
    company_id: str
    brand_identity: BrandIdentityModel


class TrendIntelligenceAgent(BaseAgent):
    name = "trend"

    def __init__(self):
        self._claude = ClaudeService()
        self._tavily = TavilyService()
        self._scraper = ScraperService()
        self._embed = EmbeddingService()
        self._pinecone = PineconeService()
        self._competitor_repo = CompetitorRepository()
        self._trend_repo = TrendRepository()

    async def run(self, input_data: TrendInput) -> TrendKnowledge:
        brand = input_data.brand_identity
        company_id = input_data.company_id

        # Search for trends and competitors
        search_query = f"{brand.industry} top competitors trends {datetime.utcnow().year}"
        results = self._tavily.search(search_query, max_results=15)

        # Try to scrape top competitor URLs
        competitor_content = []
        for r in results[:3]:
            url = r.get("url", "")
            if url:
                try:
                    text = await self._scraper.scrape_static(url)
                    competitor_content.append({"url": url, "text": text[:1000]})
                except Exception as e:
                    logger.warning("Scrape failed for %s: %s", url, e)

        # Claude reasons about trends and competitor tiers
        variables = {
            "industry": brand.industry,
            "company_id": company_id,
            "search_results": json.dumps([{"title": r.get("title"), "content": r.get("content", "")[:300]} for r in results], indent=2),
            "competitor_content": json.dumps(competitor_content, indent=2),
        }
        result = await self._claude.generate_structured(
            "trend_reasoning.md", variables, _TrendReasoningOutput
        )

        # Persist competitor profiles
        for camp in result.competitor_campaigns:
            name = camp.get("name", "unknown")
            tier = result.competitor_tiers.get(name, "secondary")
            profile = CompetitorProfile(
                competitor_id=str(uuid.uuid4()),
                company_id=company_id,
                name=name,
                tier=tier,
                industry=brand.industry,
                tone=[],
                messaging_pillars=[camp.get("key_message", "")],
                sample_content_refs=[camp.get("content_ref", "")],
                last_scanned_at=datetime.utcnow(),
            )
            await self._competitor_repo.save(profile)

            # Embed competitor profile and upsert
            summary = f"{name} {tier} competitor in {brand.industry}. {camp.get('key_message', '')}"
            vector = self._embed.embed(summary)
            self._pinecone.upsert(
                index_name=settings.pinecone_index_competitor,
                namespace=company_id,
                vector_id=profile.competitor_id,
                vector=vector,
                metadata={"competitor_id": profile.competitor_id, "tier": tier, "industry": brand.industry},
            )

        knowledge = TrendKnowledge(
            company_id=company_id,
            industry_trends=result.industry_trends,
            emerging_topics=result.emerging_topics,
            competitor_campaigns=result.competitor_campaigns,
            trending_hashtags=result.trending_hashtags,
            seasonal_events=result.seasonal_events,
            fetched_at=datetime.utcnow(),
        )
        await self._trend_repo.save(knowledge)
        return knowledge


class _TrendReasoningOutput(BaseModel):
    industry_trends: list[str]
    emerging_topics: list[str]
    competitor_campaigns: list[dict]
    trending_hashtags: list[str]
    seasonal_events: list[dict]
    competitor_tiers: dict[str, str]
