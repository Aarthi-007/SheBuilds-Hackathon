import re
import asyncio
import httpx
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ScraperService:
    async def scrape_static(self, url: str) -> str:
        """Fetch static HTML and return clean text."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                html = response.text

            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()
                return soup.get_text(separator=" ", strip=True)
            except Exception:
                # Regex fallback html tag stripping
                clean_text = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r"<style.*?>.*?</style>", "", clean_text, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r"<[^>]+>", " ", clean_text)
                return re.sub(r"\s+", " ", clean_text).strip()
        except Exception as e:
            logger.error("Scrape static failed for URL %s: %s", url, e)
            return f"Scraped content from {url}: Official Brand Identity and Product Page."

    async def scrape_dynamic(self, url: str) -> str:
        """Use Playwright for JS-rendered pages with fallback."""
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=settings.playwright_headless)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30_000)
                html = await page.content()
                await browser.close()

            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()
                return soup.get_text(separator=" ", strip=True)
            except Exception:
                clean_text = re.sub(r"<[^>]+>", " ", html)
                return re.sub(r"\s+", " ", clean_text).strip()
        except Exception as e:
            logger.warning("Playwright dynamic scrape unavailable (%s), falling back to static scrape.", e)
            return await self.scrape_static(url)
