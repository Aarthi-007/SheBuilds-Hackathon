from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from routes.opportunity_routes import router as opportunity_router
from routes.notification_routes import router as notification_router
from routes.knowledge_base_routes import router as knowledge_base_router
from orchestrator.scheduler import scheduler, register_opportunity_scan_job
from agents.opportunity_agent import OpportunityAgent
from services.news_service import NewsService
from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService
from services.claude_service import ClaudeService
from services.notification_service import NotificationService
from repositories.opportunity_repository import OpportunityRepository
from repositories.brand_repository import BrandRepository
from repositories.company_repository import CompanyRepository

from config.constants import PINECONE_INDEX_BRAND, PINECONE_INDEX_CAMPAIGN

logging.basicConfig(level=settings.LOG_LEVEL)

# Shared agent instance — imported by opportunity_routes to avoid rebuilding services per request
shared_agent: OpportunityAgent


def build_opportunity_agent() -> OpportunityAgent:
    return OpportunityAgent(
        news_service=NewsService(),
        embedding_service=EmbeddingService(),
        pinecone_service=PineconeService(),
        claude_service=ClaudeService(),
        notification_service=NotificationService(),
        opportunity_repository=OpportunityRepository(),
        brand_repository=BrandRepository(),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global shared_agent
    # Ensure Pinecone indices exist with the correct 384-dim spec before the agent runs
    pinecone_svc = PineconeService()
    pinecone_svc.ensure_index(PINECONE_INDEX_BRAND)
    pinecone_svc.ensure_index(PINECONE_INDEX_CAMPAIGN)

    shared_agent = build_opportunity_agent()
    register_opportunity_scan_job(shared_agent, CompanyRepository())
    scheduler.start()
    logging.getLogger("main").info(
        "Background trend scan started — interval: %d min", settings.SCAN_INTERVAL_MINUTES
    )
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="Klyro — Trends & Opportunities API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(opportunity_router)
app.include_router(notification_router)
app.include_router(knowledge_base_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
