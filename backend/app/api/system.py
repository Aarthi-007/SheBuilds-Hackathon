import logging
from fastapi import APIRouter, HTTPException
from app.ai.model_manager import model_manager
from app.config import settings
from app.database import get_client

logger = logging.getLogger("uvicorn")

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/models")
async def get_model_status():
    status = model_manager.get_status()
    ocr_status = status.get("paddleocr", False) or status.get("ocr", False)
    gpu_status = status.get("gpu_available", False) or status.get("gpu", False)
    return {
        "qwen": status.get("qwen", False),
        "whisper": status.get("whisper", False),
        "ocr": ocr_status,
        "paddleocr": ocr_status,
        "pymupdf": status.get("pymupdf", False),
        "sentence_transformer": status.get("sentence_transformer", False) or status.get("bge_m3", False),
        "bge_m3": status.get("bge_m3", False),
        "gpu": gpu_status,
        "gpu_available": gpu_status,
        "device": status.get("device", "cpu"),
        "ffmpeg": status.get("ffmpeg", False)
    }

@router.get("/database")
async def get_database_status():
    client = get_client()
    try:
        if hasattr(client, "admin") and hasattr(client.admin, "command"):
            await client.admin.command("ping")
        server_name = getattr(client, "address", None) or "unknown"
        return {
            "status": "ok",
            "database": "connected",
            "service": settings.PROJECT_NAME,
            "host": str(server_name)
        }
    except Exception as exc:
        logger.error("Database health check failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=503, detail="Database connection unavailable")
