"""
Notification routes — surface opportunity alerts to the frontend.

GET  /api/v1/notifications/{company_id}          — list alerts (newest first)
PATCH /api/v1/notifications/{notification_id}/read — mark one as read
GET  /api/v1/notifications/{company_id}/stream    — SSE stream for live push
"""

import asyncio
import json
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from services.notification_service import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("/{company_id}/stream")
async def notification_stream(company_id: str):
    """
    Server-Sent Events stream.
    Polls for unread notifications every 15 seconds and pushes them to the client.
    The frontend connects once and receives live alerts without polling.
    """
    svc = NotificationService()

    async def _generate():
        sent_ids: set[str] = set()
        while True:
            notifications = await svc.list_notifications(company_id, unread_only=True)
            for n in notifications:
                nid = n["notification_id"]
                if nid not in sent_ids:
                    sent_ids.add(nid)
                    yield f"data: {json.dumps(n, default=str)}\n\n"
            await asyncio.sleep(15)

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{company_id}")
async def list_notifications(company_id: str, unread_only: bool = False):
    svc = NotificationService()
    return await svc.list_notifications(company_id, unread_only=unread_only)


@router.patch("/{notification_id}/read")
async def mark_read(notification_id: str):
    svc = NotificationService()
    await svc.mark_read(notification_id)
    return {"ok": True}
