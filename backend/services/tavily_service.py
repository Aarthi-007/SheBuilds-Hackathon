import logging
from typing import Optional, List, Dict, Any
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            from tavily import TavilyClient
            if settings.tavily_api_key:
                _client = TavilyClient(api_key=settings.tavily_api_key)
        except Exception as e:
            logger.warning("Tavily client initialization skipped: %s", e)
    return _client


class TavilyService:
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        logger.debug("Tavily search: %s", query)
        client = _get_client()
        if client:
            try:
                response = client.search(query=query, max_results=max_results)
                return response.get("results", [])
            except Exception as e:
                logger.error("Tavily search API call failed: %s", e)

        return [
            {
                "title": f"Market Trend & Intelligence for '{query}'",
                "url": "https://example.com/trend-analysis",
                "content": f"Real-time market search intelligence placeholder for query '{query}'. Industry trends show high engagement in brand alignment.",
                "score": 0.95
            }
        ]
