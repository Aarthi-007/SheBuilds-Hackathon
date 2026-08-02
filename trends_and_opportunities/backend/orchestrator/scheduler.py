"""
Scheduler for the Trends & Opportunities background tracking loop.

Runs every SCAN_INTERVAL_MINUTES (default 30) for every company in the DB.
Each run fetches fresh news, deduplicates against already-seen articles,
similarity-matches against the brand knowledge base, and fires notifications
for any opportunity hits — all without manual intervention.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.settings import settings
from schemas.opportunity_report import TrackOpportunitiesRequest
from agents.opportunity_agent import OpportunityAgent
from repositories.company_repository import CompanyRepository

scheduler = AsyncIOScheduler()


def register_opportunity_scan_job(agent: OpportunityAgent, company_repo: CompanyRepository):
    """Register the continuous background scan job.

    Interval is controlled by settings.SCAN_INTERVAL_MINUTES (default 30).
    Deduplication inside OpportunityAgent ensures repeat runs never double-process
    the same article.
    """

    async def _job():
        companies = await company_repo.list_all()
        for company in companies:
            try:
                await agent.run(
                    TrackOpportunitiesRequest(
                        company_id=company.company_id,
                        industry_keywords=company.industry_keywords,
                    )
                )
            except Exception as exc:
                # Log and continue — one company failing shouldn't stop the rest
                import logging
                logging.getLogger("scheduler").error(
                    "Opportunity scan failed for %s: %s", company.company_id, exc
                )

    scheduler.add_job(
        _job,
        "interval",
        minutes=settings.SCAN_INTERVAL_MINUTES,
        id="trend_opportunity_scan",
        replace_existing=True,
    )
