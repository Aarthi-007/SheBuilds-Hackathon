"""
Knowledge base routes — manage brand identity documents.

POST /api/v1/knowledge-base/brand          — upsert a brand knowledge document
GET  /api/v1/knowledge-base/brand/{company_id} — fetch current brand knowledge
"""

from fastapi import APIRouter, HTTPException

from schemas.brand_identity import BrandIdentityModel
from repositories.brand_repository import BrandRepository

router = APIRouter(prefix="/api/v1/knowledge-base", tags=["knowledge-base"])


@router.post("/brand", status_code=201)
async def upsert_brand_knowledge(payload: BrandIdentityModel):
    """Upload or update the brand knowledge document for a company."""
    repo = BrandRepository()
    await repo.upsert(payload)
    return {"ok": True, "company_id": payload.company_id, "version": payload.version}


@router.get("/brand/{company_id}")
async def get_brand_knowledge(company_id: str):
    """Fetch the latest brand knowledge for a company."""
    repo = BrandRepository()
    doc = await repo.get(company_id)
    if not doc:
        raise HTTPException(status_code=404, detail="No brand knowledge found for this company.")
    return doc
