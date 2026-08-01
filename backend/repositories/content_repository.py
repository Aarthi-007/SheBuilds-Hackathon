from database.mongo_client import get_db
from schemas.universal_content import UniversalContent
from config.constants import COL_UNIVERSAL_CONTENT


class ContentRepository:
    def __init__(self):
        self._col = get_db()[COL_UNIVERSAL_CONTENT]

    async def save(self, content: UniversalContent) -> None:
        await self._col.replace_one(
            {"content_id": content.content_id},
            content.model_dump(),
            upsert=True,
        )

    async def get_by_id(self, content_id: str) -> UniversalContent | None:
        doc = await self._col.find_one({"content_id": content_id})
        if doc is None:
            return None
        doc.pop("_id", None)
        return UniversalContent(**doc)

    async def list_by_company(self, company_id: str, limit: int = 50) -> list[UniversalContent]:
        cursor = self._col.find({"company_id": company_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [UniversalContent(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]
