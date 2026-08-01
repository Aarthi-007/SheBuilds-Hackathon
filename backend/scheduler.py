"""
APScheduler background jobs.
Import and start from main.py lifespan if needed.
"""
import logging
from utils.logger import get_logger

logger = get_logger(__name__)

_scheduler = None


def get_scheduler():
    global _scheduler
    if _scheduler is None:
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            _scheduler = AsyncIOScheduler()

            @_scheduler.scheduled_job("cron", hour=3, minute=0)
            async def daily_trend_refresh():
                from database.mongo_client import get_db
                from config.constants import COL_COMPANIES
                from dependencies import get_orchestrator
                from orchestrator.orchestrator_agent import OrchestratorRequest
                from config.constants import WORKFLOW_COMPETITOR_SCAN
                from repositories.brand_repository import BrandRepository

                db = get_db()
                brand_repo = BrandRepository()
                companies = await db[COL_COMPANIES].find({}, {"company_id": 1}).to_list(length=500)

                orchestrator = get_orchestrator()
                for company in companies:
                    cid = company.get("company_id")
                    brand = await brand_repo.get_by_company(cid)
                    if brand is None:
                        continue
                    try:
                        await orchestrator.run(
                            OrchestratorRequest(
                                workflow=WORKFLOW_COMPETITOR_SCAN,
                                inputs={"company_id": cid, "brand_identity": brand.model_dump()},
                            )
                        )
                        logger.info("Daily trend refresh complete for %s", cid)
                    except Exception as exc:
                        logger.error("Daily trend refresh failed for %s: %s", cid, exc)

        except Exception as e:
            logger.warning("APScheduler background scheduler unavailable: %s", e)
            _scheduler = None
    return _scheduler


def start():
    sched = get_scheduler()
    if sched:
        sched.start()
        logger.info("Scheduler started.")
