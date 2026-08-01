from database.mongo_client import get_db
from schemas.competitor_profile import CompetitorProfile
from config.constants import COL_COMPETITOR_PROFILES


class CompetitorRepository:
    def __init__(self):
        self._col = get_db()[COL_COMPETITOR_PROFILES]

    async def save(self, profile: CompetitorProfile) -> None:
        await self._col.replace_one(
            {"competitor_id": profile.competitor_id},
            profile.model_dump(),
            upsert=True,
        )

    async def get_by_id(self, competitor_id: str) -> CompetitorProfile | None:
        doc = await self._col.find_one({"competitor_id": competitor_id})
        if doc is None:
            return None
        doc.pop("_id", None)
        return CompetitorProfile(**doc)

    async def list_by_company(self, company_id: str) -> list[CompetitorProfile]:
        cursor = self._col.find({"company_id": company_id})
        docs = await cursor.to_list(length=200)
        return [CompetitorProfile(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]
