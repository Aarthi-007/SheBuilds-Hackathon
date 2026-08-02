"""
NewsService — wraps a News API (newsapi.org by default) for the "keep tracking trends"
background step of the Trends & Opportunities layer.

Only this service talks to the News API. Agents never call requests/httpx directly (context.md rule).
"""

import httpx
from datetime import datetime, timedelta

from config.settings import settings


class NewsService:
    BASE_URL = "https://newsapi.org/v2/everything"

    async def fetch_trending(
        self,
        query: str,
        since_hours: int = 24,
        page_size: int = 20,
    ) -> list[dict]:
        """
        Fetch recent news articles matching `query` (e.g. company's industry + core keywords).
        Returns raw article dicts: {headline, summary, source, url, published_at}.
        """
        since = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat()
        params = {
            "q": query,
            "from": since,
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "language": "en",
            "apiKey": settings.NEWS_API_KEY,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        return [
            {
                "headline": a["title"],
                "summary": a.get("description") or "",
                "source": a["source"]["name"],
                "url": a["url"],
                "published_at": a["publishedAt"],
            }
            for a in data.get("articles", [])
        ]
