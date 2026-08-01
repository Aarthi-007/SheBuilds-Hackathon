from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from app.models.brand import Brand
from app.models.campaign import Campaign, CampaignVersion
from app.schemas.campaign import CampaignCreateRequest

class CampaignService:
    @staticmethod
    async def create_campaign(org_id: str, user_id: str, req: CampaignCreateRequest) -> Tuple[Campaign, CampaignVersion]:
        brand = await Brand.get(req.brand_id)
        if not brand or brand.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        campaign = Campaign(
            brand_id=req.brand_id,
            title=req.title,
            description=req.description,
            platform=req.platform,
            objective=req.objective,
            status="draft",
            current_version=1,
            created_by=user_id
        )
        await campaign.insert()

        version = CampaignVersion(
            campaign_id=str(campaign.id),
            version=1,
            text_content=req.text_content or f"{req.title} - {req.description or ''}",
            generated_by="User Created"
        )
        await version.insert()

        return campaign, version

    @staticmethod
    async def get_campaigns_by_brand(brand_id: str, org_id: str) -> List[Campaign]:
        brand = await Brand.get(brand_id)
        if not brand or brand.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
        return await Campaign.find({"brand_id": brand_id}).to_list()

    @staticmethod
    async def get_campaign_by_id(campaign_id: str) -> Tuple[Campaign, List[CampaignVersion]]:
        campaign = await Campaign.get(campaign_id)
        if not campaign:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
        versions = await CampaignVersion.find({"campaign_id": campaign_id}).to_list()
        return campaign, versions
