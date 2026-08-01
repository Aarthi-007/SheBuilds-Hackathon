from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.schemas.auth import StandardResponse
from app.models.identity import AIMemory
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/memory", tags=["Module 7 - AI Memory Engine"])

class MemoryStoreRequest(BaseModel):
    brand_id: str
    entity_type: str
    entity_id: str
    content_text: str
    summary: str

class MemorySearchRequest(BaseModel):
    brand_id: str
    query: str
    limit: int = 5

@router.post("/store", response_model=StandardResponse)
async def store_memory(req: MemoryStoreRequest, current_user: User = Depends(get_current_user)):
    memory = AIMemory(
        brand_id=req.brand_id,
        entity_type=req.entity_type,
        entity_id=req.entity_id,
        content_text=req.content_text,
        summary=req.summary
    )
    await memory.insert()
    return StandardResponse(success=True, message="Semantic memory stored successfully", data={"memory_id": str(memory.id)})

@router.post("/search", response_model=StandardResponse)
async def search_memory(req: MemorySearchRequest, current_user: User = Depends(get_current_user)):
    memories = await AIMemory.find({"brand_id": req.brand_id}).limit(req.limit).to_list()
    results = [
        {
            "id": str(m.id),
            "entity_type": m.entity_type,
            "entity_id": m.entity_id,
            "summary": m.summary,
            "content_text": m.content_text
        }
        for m in memories
    ]
    return StandardResponse(success=True, data=results)
