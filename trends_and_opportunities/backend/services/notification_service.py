"""
NotificationService — creates and stores opportunity alerts.
When the agent finds a match with is_opportunity=True, it calls notify().
Consumers poll GET /api/v1/notifications/{company_id} or listen on the SSE stream.
"""

import uuid
from datetime import datetime

from database.mongo_client import get_db
from schemas.opportunity_report import OpportunityReport


class NotificationService:
    def __init__(self):
        self._db = get_db()

    async def notify(self, report: OpportunityReport, headline: str = "") -> None:
        """Persist a notification doc for an opportunity hit."""
        if not report.is_opportunity:
            return
        notification = {
            "notification_id": str(uuid.uuid4()),
            "company_id": report.company_id,
            "report_id": report.report_id,
            "signal_id": report.signal_id,
            "headline": headline or report.reasoning[:120],
            "brand_fit_score": report.brand_fit_score,
            "confidence": report.confidence,
            "recommendations_count": len(report.recommendations),
            "read": False,
            "created_at": datetime.utcnow(),
        }
        await self._db.notifications.insert_one(notification)

    async def list_notifications(
        self, company_id: str, unread_only: bool = False
    ) -> list[dict]:
        query: dict = {"company_id": company_id}
        if unread_only:
            query["read"] = False
        cursor = self._db.notifications.find(query).sort("created_at", -1).limit(50)
        docs = [doc async for doc in cursor]
        for doc in docs:
            doc.pop("_id", None)
        return docs

    async def mark_read(self, notification_id: str) -> None:
        await self._db.notifications.update_one(
            {"notification_id": notification_id},
            {"$set": {"read": True}},
        )
