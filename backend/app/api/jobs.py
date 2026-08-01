from fastapi import APIRouter, Depends
from app.schemas.auth import StandardResponse
from app.services.job_service import JobService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/jobs", tags=["Module 10 - Background Jobs & Workers"])

@router.get("/{job_id}", response_model=StandardResponse)
async def get_job_status(job_id: str, current_user: User = Depends(get_current_user)):
    job = await JobService.get_job(job_id)
    return StandardResponse(
        success=True,
        data={
            "id": str(job.id),
            "brand_id": job.brand_id,
            "job_type": job.job_type,
            "status": job.status,
            "progress": job.progress,
            "current_stage": job.current_stage,
            "result_reference": job.result_reference,
            "started_at": job.started_at.isoformat()
        }
    )

@router.delete("/{job_id}", response_model=StandardResponse)
async def cancel_job(job_id: str, current_user: User = Depends(get_current_user)):
    await JobService.cancel_job(job_id)
    return StandardResponse(success=True, message="Job cancelled successfully")
