import asyncio
from utils.logger import get_logger

logger = get_logger(__name__)


async def async_retry(coro_fn, *args, max_attempts: int = 3, delay: float = 1.0, **kwargs):
    """Retry an async callable up to max_attempts times with exponential backoff."""
    for attempt in range(1, max_attempts + 1):
        try:
            return await coro_fn(*args, **kwargs)
        except Exception as exc:
            if attempt == max_attempts:
                raise
            wait = delay * (2 ** (attempt - 1))
            logger.warning("Attempt %d/%d failed: %s. Retrying in %.1fs…", attempt, max_attempts, exc, wait)
            await asyncio.sleep(wait)
