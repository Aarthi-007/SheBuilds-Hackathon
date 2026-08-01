from fastapi import APIRouter
from app.ai.model_manager import model_manager

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
