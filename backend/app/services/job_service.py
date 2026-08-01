import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status, BackgroundTasks
from app.models.job import Job

logger = logging.getLogger("uvicorn")


class JobService:
    """
    Background Job Queue & Worker Manager for Klyros.
    
    States: Pending -> Processing -> Completed / Failed
    """

    @staticmethod
    async def create_job(brand_id: str, job_type: str = "Identity") -> Job:
        """Create a new job record with state 'Pending'."""
        job = Job(
            brand_id=brand_id,
            job_type=job_type,
            status="Pending",
            progress=0,
            current_stage="Queued for Processing"
        )
        await job.insert()
        return job

    @classmethod
    async def run_identity_job_worker(cls, job_id: str, brand_id: str, org_id: str, groq_api_key: Optional[str] = None) -> None:
        """Asynchronous background worker executing Feature Extraction & Brand Identity synthesis."""
        job = await Job.get(job_id)
        if not job:
            return

        try:
            # Stage 1: Processing
            job.status = "Processing"
            job.progress = 25
            job.current_stage = "Feature Extraction into FeatureStore"
            await job.save()

            # Import dynamically to avoid circular import
            from app.services.identity_service import IdentityService
            
            # Stage 2: Feature Extraction & Identity Building
            identity, _ = await IdentityService.build_identity(
                brand_id=brand_id,
                org_id=org_id,
                force_rebuild=True,
                groq_api_key=groq_api_key
            )

            # Stage 3: Completed
            job.status = "Completed"
            job.progress = 100
            job.current_stage = "Living Brand Identity Synthesized and Saved"
            job.result_reference = {"identity_id": str(identity.id)}
            job.completed_at = datetime.now(timezone.utc)
            await job.save()

        except Exception as e:
            logger.error("Error in background job worker for job %s: %s", job_id, e)
            job.status = "Failed"
            job.error = str(e)
            job.completed_at = datetime.now(timezone.utc)
            await job.save()

    @staticmethod
    async def get_job(job_id: str) -> Job:
        job = await Job.get(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return job

    @staticmethod
    async def list_jobs_by_brand(brand_id: str) -> List[Job]:
        return await Job.find(Job.brand_id == brand_id).sort("-started_at").to_list()

    @staticmethod
    async def cancel_job(job_id: str) -> bool:
        job = await JobService.get_job(job_id)
        job.status = "Failed"
        job.error = "Cancelled by user"
        job.completed_at = datetime.now(timezone.utc)
        await job.save()
        return True
