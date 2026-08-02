from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""

    MONGODB_URI: str = ""
    MONGODB_DB_NAME: str = "klyro"

    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = ""
    PINECONE_INDEX_BRAND: str = "klyro-brand-identity"
    PINECONE_INDEX_COMPETITOR: str = "klyro-competitors"
    PINECONE_INDEX_CAMPAIGN: str = "klyro-campaigns"

    TAVILY_API_KEY: str = ""
    NEWS_API_KEY: str = ""          # new: for the Trends & Opportunities layer
    PLAYWRIGHT_HEADLESS: bool = True

    SCAN_INTERVAL_MINUTES: int = 30   # how often the background trend scan runs

    APP_ENV: str = "development"
    APP_PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    JWT_SECRET: str = ""
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
