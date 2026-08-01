from fastapi import APIRouter, HTTPException, Depends
from schemas.trend_knowledge import TrendKnowledge
from repositories.trend_repository import TrendRepository

router = APIRouter(prefix="/trends", tags=["trends"])


def _repo():
    return TrendRepository()


@router.get("/{company_id}", response_model=TrendKnowledge)
async def get_trends(company_id: str, repo: TrendRepository = Depends(_repo)):
    knowledge = await repo.get_latest(company_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="No trend data found")
    return knowledge
