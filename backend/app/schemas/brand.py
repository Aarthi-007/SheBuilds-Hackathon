from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class BrandCreateRequest(BaseModel):
    name: str
    industry: str
    website: Optional[str] = None
    description: Optional[str] = None
    languages: Optional[List[str]] = ["English"]

class BrandUpdateRequest(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    languages: Optional[List[str]] = None
    logo_path: Optional[str] = None

class BrandDTO(BaseModel):
    id: str
    organization_id: str
    name: str
    industry: str
    website: Optional[str] = None
    description: Optional[str] = None
    languages: List[str] = ["English"]
    logo_path: Optional[str] = None
    status: str
    created_at: str

class BrandAssetDTO(BaseModel):
    id: str
    brand_id: str
    asset_name: str
    asset_type: str
    category: str
    storage_url: str
    file_size: int
    mime_type: str
    processing_status: str
    metadata: Dict[str, Any]
    created_at: str
