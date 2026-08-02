"""
BrandRepository — reads the brand knowledge base from MongoDB.

The brand_knowledge collection is the source of truth for a company's identity:
tone, values, messaging pillars, target audience, visual identity etc.
Documents are upserted here whenever the brand assets are updated (manual upload
or Brand Identity Agent refresh). This layer only reads — writes are owned by
whoever manages the knowledge base.
"""

from database.mongo_client import get_db
from schemas.brand_identity import BrandIdentityModel


class BrandRepository:
    COLLECTION = "brand_knowledge"

    def __init__(self):
        self._db = get_db()

    async def get(self, company_id: str) -> BrandIdentityModel | None:
        """Fetch the latest brand knowledge doc for a company."""
        doc = await self._db[self.COLLECTION].find_one(
            {"company_id": company_id},
            sort=[("version", -1)],   # always use the most recent version
        )
        if not doc:
            return None
        doc.pop("_id", None)
        return BrandIdentityModel(**doc)

    async def upsert(self, model: BrandIdentityModel) -> None:
        """Write or replace a brand knowledge entry (called by the knowledge base uploader)."""
        await self._db[self.COLLECTION].update_one(
            {"company_id": model.company_id, "version": model.version},
            {"$set": model.model_dump()},
            upsert=True,
        )
