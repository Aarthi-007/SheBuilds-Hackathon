from database.mongo_client import get_db
from schemas.campaign_memory import CampaignMemory
from config.constants import COL_CAMPAIGN_MEMORY


class CampaignRepository:
    def __init__(self):
        self._col = get_db()[COL_CAMPAIGN_MEMORY]

    async def save(self, campaign: CampaignMemory) -> None:
        await self._col.replace_one(
            {"campaign_id": campaign.campaign_id},
            campaign.model_dump(),
            upsert=True,
        )

    async def get_by_id(self, campaign_id: str) -> CampaignMemory | None:
        doc = await self._col.find_one({"campaign_id": campaign_id})
        if doc is None:
            return None
        doc.pop("_id", None)
        return CampaignMemory(**doc)

    async def list_by_company(self, company_id: str) -> list[CampaignMemory]:
        cursor = self._col.find({"company_id": company_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [CampaignMemory(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]
