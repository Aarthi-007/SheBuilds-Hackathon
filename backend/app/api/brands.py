from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.schemas.auth import StandardResponse
from app.schemas.brand import BrandCreateRequest, BrandUpdateRequest, BrandDTO, BrandAssetDTO
from app.services.brand_service import BrandService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/brands", tags=["Module 2 - Brand & Asset Management"])

@router.post("", response_model=StandardResponse)
async def create_brand(req: BrandCreateRequest, current_user: User = Depends(get_current_user)):
    brand = await BrandService.create_brand(current_user.organization_id, str(current_user.id), req)
    dto = BrandDTO(
        id=str(brand.id),
        organization_id=brand.organization_id,
        name=brand.name,
        industry=brand.industry,
        website=brand.website,
        description=brand.description,
        languages=brand.languages,
        logo_path=brand.logo_path,
        status=brand.status,
        created_at=brand.created_at.isoformat()
    )
    return StandardResponse(success=True, message="Brand created successfully", data=dto)

@router.get("", response_model=StandardResponse)
async def get_brands(current_user: User = Depends(get_current_user)):
    brands = await BrandService.get_brands_for_org(current_user.organization_id)
    dtos = [
        BrandDTO(
            id=str(b.id),
            organization_id=b.organization_id,
            name=b.name,
            industry=b.industry,
            website=b.website,
            description=b.description,
            languages=b.languages,
            logo_path=b.logo_path,
            status=b.status,
            created_at=b.created_at.isoformat()
        )
        for b in brands
    ]
    return StandardResponse(success=True, data=dtos)

@router.get("/{brand_id}", response_model=StandardResponse)
async def get_brand(brand_id: str, current_user: User = Depends(get_current_user)):
    brand = await BrandService.get_brand_by_id(brand_id, current_user.organization_id)
    dto = BrandDTO(
        id=str(brand.id),
        organization_id=brand.organization_id,
        name=brand.name,
        industry=brand.industry,
        website=brand.website,
        description=brand.description,
        languages=brand.languages,
        logo_path=brand.logo_path,
        status=brand.status,
        created_at=brand.created_at.isoformat()
    )
    return StandardResponse(success=True, data=dto)

@router.put("/{brand_id}", response_model=StandardResponse)
async def update_brand(brand_id: str, req: BrandUpdateRequest, current_user: User = Depends(get_current_user)):
    brand = await BrandService.update_brand(brand_id, current_user.organization_id, req)
    dto = BrandDTO(
        id=str(brand.id),
        organization_id=brand.organization_id,
        name=brand.name,
        industry=brand.industry,
        website=brand.website,
        description=brand.description,
        languages=brand.languages,
        logo_path=brand.logo_path,
        status=brand.status,
        created_at=brand.created_at.isoformat()
    )
    return StandardResponse(success=True, message="Brand updated", data=dto)

@router.delete("/{brand_id}", response_model=StandardResponse)
async def delete_brand(brand_id: str, current_user: User = Depends(get_current_user)):
    await BrandService.delete_brand(brand_id, current_user.organization_id)
    return StandardResponse(success=True, message="Brand deleted successfully")

@router.post("/{brand_id}/assets", response_model=StandardResponse)
async def upload_brand_assets(
    brand_id: str,
    files: List[UploadFile] = File(...),
    category: str = Form("Advertisements"),
    current_user: User = Depends(get_current_user)
):
    assets, job = await BrandService.upload_brand_assets(brand_id, current_user.organization_id, files, category=category)
    asset_dtos = [
        BrandAssetDTO(
            id=str(a.id),
            brand_id=a.brand_id,
            asset_name=a.asset_name,
            asset_type=a.asset_type,
            category=a.category,
            storage_url=a.storage_url,
            file_size=a.file_size,
            mime_type=a.mime_type,
            processing_status=a.processing_status,
            metadata=a.metadata,
            created_at=a.created_at.isoformat()
        )
        for a in assets
    ]
    return StandardResponse(
        success=True,
        message=f"Uploaded {len(assets)} assets successfully",
        data={"assets": asset_dtos, "job_id": str(job.id)}
    )

@router.get("/{brand_id}/assets", response_model=StandardResponse)
async def get_brand_assets(brand_id: str, current_user: User = Depends(get_current_user)):
    assets = await BrandService.get_brand_assets(brand_id, current_user.organization_id)
    dtos = [
        BrandAssetDTO(
            id=str(a.id),
            brand_id=a.brand_id,
            asset_name=a.asset_name,
            asset_type=a.asset_type,
            category=a.category,
            storage_url=a.storage_url,
            file_size=a.file_size,
            mime_type=a.mime_type,
            processing_status=a.processing_status,
            metadata=a.metadata,
            created_at=a.created_at.isoformat()
        )
        for a in assets
    ]
    return StandardResponse(success=True, data=dtos)
