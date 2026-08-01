from database.mongo_client import get_db
from schemas.brand_identity import BrandIdentityModel
from config.constants import COL_BRAND_IDENTITY, COL_BRAND_IDENTITY_HISTORY


class BrandRepository:
    def __init__(self):
        self._col = get_db()[COL_BRAND_IDENTITY]
        self._history_col = get_db()[COL_BRAND_IDENTITY_HISTORY]

    async def save(self, model: BrandIdentityModel) -> None:
        # archive current version before overwriting
        existing = await self.get_by_company(model.company_id)
        if existing:
            await self._history_col.insert_one(
                {"company_id": existing.company_id, "version": existing.version, "snapshot": existing.model_dump()}
            )
        await self._col.replace_one(
            {"company_id": model.company_id},
            model.model_dump(),
            upsert=True,
        )

    async def get_by_company(self, company_id: str) -> BrandIdentityModel | None:
        doc = await self._col.find_one({"company_id": company_id})
        if doc is None:
            return None
        doc.pop("_id", None)
        return BrandIdentityModel(**doc)
