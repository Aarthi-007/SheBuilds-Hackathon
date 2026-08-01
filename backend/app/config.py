import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Klyros Backend API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB Config
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "klyros")
    
    # JWT Config
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-klyros-hackathon-key-2026")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI provider config
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "qwen").lower()
    VISION_PROVIDER: str = os.getenv("VISION_PROVIDER", AI_PROVIDER).lower()
    TEXT_PROVIDER: str = os.getenv("TEXT_PROVIDER", AI_PROVIDER).lower()

    # Groq API Config (backward compatible)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_VISION_MODEL: str = os.getenv("GROQ_VISION_MODEL", "llama-3.3-70b-versatile")
    GROQ_TEXT_MODEL: str = os.getenv("GROQ_TEXT_MODEL", "llama-3.3-70b-versatile")

    # Qwen2.5-VL API Config
    QWEN_API_KEY: Optional[str] = os.getenv("QWEN_API_KEY", None)
    QWEN_BASE_URL: str = os.getenv("QWEN_BASE_URL", "https://api.together.xyz/v1")
    QWEN_VISION_MODEL: str = os.getenv("QWEN_VISION_MODEL", "Qwen/Qwen2.5-VL-7B-Instruct")
    QWEN_TEXT_MODEL: str = os.getenv("QWEN_TEXT_MODEL", "Qwen/Qwen2.5-7B-Instruct")

    # OpenAI-compatible provider aliases
    VISION_API_KEY: Optional[str] = os.getenv("VISION_API_KEY", None)
    VISION_BASE_URL: str = os.getenv("VISION_BASE_URL", GROQ_BASE_URL)
    VISION_MODEL: str = os.getenv("VISION_MODEL", GROQ_VISION_MODEL)

    TEXT_API_KEY: Optional[str] = os.getenv("TEXT_API_KEY", None)
    TEXT_BASE_URL: str = os.getenv("TEXT_BASE_URL", GROQ_BASE_URL)
    TEXT_MODEL: str = os.getenv("TEXT_MODEL", GROQ_TEXT_MODEL)
    
    # Local & Pipeline Model Configs
    SKIP_HF_DOWNLOAD: bool = os.getenv("SKIP_HF_DOWNLOAD", "true").lower() == "true"
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "tiny")
    PADDLE_OCR_LANG: str = os.getenv("PADDLE_OCR_LANG", "en")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

    # Storage Config
    STORAGE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def __getattr__(self, name: str):
        legacy_aliases = {
            "mongodb_uri": "MONGODB_URI",
            "mongodb_db_name": "DATABASE_NAME",
            "jwt_secret": "JWT_SECRET",
            "jwt_algorithm": "JWT_ALGORITHM",
            "access_token_expire_minutes": "ACCESS_TOKEN_EXPIRE_MINUTES",
            "refresh_token_expire_days": "REFRESH_TOKEN_EXPIRE_DAYS",
            "ai_provider": "AI_PROVIDER",
            "vision_provider": "VISION_PROVIDER",
            "text_provider": "TEXT_PROVIDER",
            "groq_api_key": "GROQ_API_KEY",
            "groq_base_url": "GROQ_BASE_URL",
            "groq_vision_model": "GROQ_VISION_MODEL",
            "groq_text_model": "GROQ_TEXT_MODEL",
            "qwen_api_key": "QWEN_API_KEY",
            "qwen_base_url": "QWEN_BASE_URL",
            "qwen_vision_model": "QWEN_VISION_MODEL",
            "qwen_text_model": "QWEN_TEXT_MODEL",
            "vision_api_key": "VISION_API_KEY",
            "vision_base_url": "VISION_BASE_URL",
            "vision_model": "VISION_MODEL",
            "text_api_key": "TEXT_API_KEY",
            "text_base_url": "TEXT_BASE_URL",
            "text_model": "TEXT_MODEL",
            "whisper_model": "WHISPER_MODEL",
            "paddle_ocr_lang": "PADDLE_OCR_LANG",
            "embedding_model": "EMBEDDING_MODEL",
            "storage_dir": "STORAGE_DIR",
            "base_url": "BASE_URL",
            "project_name": "PROJECT_NAME",
            "version": "VERSION",
            "api_v1_str": "API_V1_STR",
        }

        if name in legacy_aliases:
            return getattr(self, legacy_aliases[name])

        normalized_name = name.upper()
        if normalized_name in self.__class__.__annotations__:
            return getattr(self, normalized_name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

settings = Settings()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
