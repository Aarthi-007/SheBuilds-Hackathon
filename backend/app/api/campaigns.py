from fastapi import APIRouter, Depends
from app.schemas.auth import StandardResponse
from app.schemas.campaign import CampaignCreateRequest, CampaignDTO, CampaignVersionDTO
from app.services.campaign_service import CampaignService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/campaigns", tags=["Module 8 - Campaign Management"])

@router.post("", response_model=StandardResponse)
async def create_campaign(req: CampaignCreateRequest, current_user: User = Depends(get_current_user)):
    campaign, version = await CampaignService.create_campaign(current_user.organization_id, str(current_user.id), req)
    c_dto = CampaignDTO(
        id=str(campaign.id),
        brand_id=campaign.brand_id,
        title=campaign.title,
        description=campaign.description,
        platform=campaign.platform,
        objective=campaign.objective,
        status=campaign.status,
        current_version=campaign.current_version,
        published=campaign.published,
        created_at=campaign.created_at.isoformat()
    )
    v_dto = CampaignVersionDTO(
        id=str(version.id),
        campaign_id=version.campaign_id,
        version=version.version,
        text_content=version.text_content,
        image_urls=version.image_urls,
        video_urls=version.video_urls,
        generated_by=version.generated_by,
        validation_score=version.validation_score,
        approved=version.approved,
        created_at=version.created_at.isoformat()
    )
    return StandardResponse(success=True, message="Campaign created", data={"campaign": c_dto, "version": v_dto})

@router.get("", response_model=StandardResponse)
async def get_campaigns(brand_id: str, current_user: User = Depends(get_current_user)):
    campaigns = await CampaignService.get_campaigns_by_brand(brand_id, current_user.organization_id)
    dtos = [
        CampaignDTO(
            id=str(c.id),
            brand_id=c.brand_id,
            title=c.title,
            description=c.description,
            platform=c.platform,
            objective=c.objective,
            status=c.status,
            current_version=c.current_version,
            published=c.published,
            created_at=c.created_at.isoformat()
        )
        for c in campaigns
    ]
    return StandardResponse(success=True, data=dtos)

@router.get("/{campaign_id}", response_model=StandardResponse)
async def get_campaign(campaign_id: str, current_user: User = Depends(get_current_user)):
    campaign, versions = await CampaignService.get_campaign_by_id(campaign_id)
    c_dto = CampaignDTO(
        id=str(campaign.id),
        brand_id=campaign.brand_id,
        title=campaign.title,
        description=campaign.description,
        platform=campaign.platform,
        objective=campaign.objective,
        status=campaign.status,
        current_version=campaign.current_version,
        published=campaign.published,
        created_at=campaign.created_at.isoformat()
    )
    v_dtos = [
        CampaignVersionDTO(
            id=str(v.id),
            campaign_id=v.campaign_id,
            version=v.version,
            text_content=v.text_content,
            image_urls=v.image_urls,
            video_urls=v.video_urls,
            generated_by=v.generated_by,
            validation_score=v.validation_score,
            approved=v.approved,
            created_at=v.created_at.isoformat()
        )
        for v in versions
    ]
    return StandardResponse(success=True, data={"campaign": c_dto, "versions": v_dtos})
