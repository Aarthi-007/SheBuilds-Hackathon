"""
OpportunityRepository — only place that reads/writes the `trend_signals` and
`opportunity_reports` collections. Agents/services never import mongo_client directly.
"""

from database.mongo_client import get_db
from schemas.trend_knowledge import TrendSignal
from schemas.opportunity_report import OpportunityReport


class OpportunityRepository:
    def __init__(self):
        self._db = get_db()

    async def save_signal(self, signal: TrendSignal) -> None:
        await self._db.trend_signals.update_one(
            {"signal_id": signal.signal_id},
            {"$set": signal.model_dump()},
            upsert=True,
        )

    async def save_report(self, report: OpportunityReport) -> None:
        await self._db.opportunity_reports.insert_one(report.model_dump())

    async def list_reports(self, company_id: str, only_opportunities: bool = False) -> list[dict]:
        query = {"company_id": company_id}
        if only_opportunities:
            query["is_opportunity"] = True
        cursor = self._db.opportunity_reports.find(query).sort("created_at", -1)
        docs = [doc async for doc in cursor]
        for doc in docs:
            doc.pop("_id", None)
        return docs

    async def list_reports_enriched(self, company_id: str, only_opportunities: bool = False) -> list[dict]:
        """Reports joined with their source signal to include headline, source, url."""
        reports = await self.list_reports(company_id, only_opportunities)

        # Batch-fetch the signals we need
        signal_ids = [r["signal_id"] for r in reports]
        cursor = self._db.trend_signals.find(
            {"signal_id": {"$in": signal_ids}},
            {"signal_id": 1, "headline": 1, "source": 1, "url": 1, "_id": 0},
        )
        signals = {doc["signal_id"]: doc async for doc in cursor}

        for report in reports:
            sig = signals.get(report["signal_id"], {})
            report["headline"] = sig.get("headline")
            report["source"] = sig.get("source")
            report["url"] = sig.get("url")

        return reports

    async def get_report(self, report_id: str) -> dict | None:
        doc = await self._db.opportunity_reports.find_one({"report_id": report_id})
        if doc:
            doc.pop("_id", None)
        return doc

    async def get_seen_urls(self, company_id: str) -> set[str]:
        """Return all article URLs already processed for this company (deduplication)."""
        cursor = self._db.trend_signals.find(
            {"company_id": company_id}, {"url": 1, "_id": 0}
        )
        return {doc["url"] async for doc in cursor}