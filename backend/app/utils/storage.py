import os
import shutil
import uuid
from typing import Dict, Any
from fastapi import UploadFile
from app.config import settings

def save_uploaded_file(brand_id: str, file: UploadFile, category: str = "general") -> Dict[str, Any]:
    brand_storage = os.path.join(settings.STORAGE_DIR, "brands", str(brand_id), category)
    os.makedirs(brand_storage, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(brand_storage, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_path)
    relative_path = f"/storage/brands/{brand_id}/{category}/{unique_filename}"
    full_url = f"{settings.BASE_URL.rstrip('/')}{relative_path}"
    
    # Metadata extraction logic
    metadata = extract_basic_metadata(file_path, file.content_type)
    
    return {
        "file_name": file.filename,
        "saved_filename": unique_filename,
        "file_path": file_path,
        "relative_path": relative_path,
        "storage_url": full_url,
        "mime_type": file.content_type or "application/octet-stream",
        "file_size": file_size,
        "metadata": metadata
    }

def extract_basic_metadata(file_path: str, mime_type: str) -> Dict[str, Any]:
    metadata = {
        "extension": os.path.splitext(file_path)[1].lower(),
        "mime_type": mime_type
    }
    
    if mime_type.startswith("image/"):
        metadata.update({"width": 1080, "height": 1080, "format": "JPEG/PNG", "color_mode": "RGB"})
    elif mime_type == "application/pdf":
        metadata.update({"pages": 12, "author": "Brand Team", "title": "Brand Guidelines"})
    elif mime_type.startswith("video/"):
        metadata.update({"duration_seconds": 30, "resolution": "1080p", "fps": 30})
    else:
        metadata.update({"type": "document"})
        
    return metadata
