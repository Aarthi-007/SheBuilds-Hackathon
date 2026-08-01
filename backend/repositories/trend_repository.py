from database.mongo_client import get_db
from schemas.trend_knowledge import TrendKnowledge
from config.constants import COL_TREND_KNOWLEDGE


class TrendRepository:
    def __init__(self):
        self._col = get_db()[COL_TREND_KNOWLEDGE]

    async def save(self, knowledge: TrendKnowledge) -> None:
        await self._col.insert_one(knowledge.model_dump())

    async def get_latest(self, company_id: str) -> TrendKnowledge | None:
        doc = await self._col.find_one(
            {"company_id": company_id}, sort=[("fetched_at", -1)]
        )
        if doc is None:
            return None
        doc.pop("_id", None)
        return TrendKnowledge(**doc)
