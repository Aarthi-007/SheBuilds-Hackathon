from fastapi import APIRouter
from app.ai.model_manager import model_manager

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/models")
async def get_model_status():
    status = model_manager.get_status()
    return {
        "qwen": status.get("qwen", False),
        "whisper": status.get("whisper", False),
        "paddleocr": status.get("paddleocr", False),
        "pymupdf": status.get("pymupdf", False),
        "bge_m3": status.get("bge_m3", False),
        "gpu_available": status.get("gpu_available", False),
        "device": status.get("device", "cpu"),
        "ffmpeg": status.get("ffmpeg", False)
    }
