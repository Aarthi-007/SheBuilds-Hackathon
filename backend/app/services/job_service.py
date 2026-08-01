from typing import Optional
from fastapi import HTTPException, status
from app.models.job import Job

class JobService:
    @staticmethod
    async def get_job(job_id: str) -> Job:
        job = await Job.get(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return job

    @staticmethod
    async def cancel_job(job_id: str) -> bool:
        job = await JobService.get_job(job_id)
        job.status = "failed"
        job.error = "Cancelled by user"
        await job.save()
        return True
