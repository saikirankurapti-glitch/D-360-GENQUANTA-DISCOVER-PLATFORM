import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
# Import models to ensure they are registered with SQLAlchemy Base
from app.models.copilot import ChatSession, ChatMessage
from app.services.rag_service import rag_service

# Initialize Database tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ingest platform data in the background
    logger.info("Initializing scientific knowledge RAG indexes...")
    try:
        await rag_service.ingest_platform_data()
    except Exception as err:
        logger.warning(f"Initial dynamic knowledge ingestion failed, using fallback: {err}")
    yield
    # Shutdown logic
    logger.info("Scientific knowledge index shut down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.endpoints.copilot import router as copilot_router
app.include_router(copilot_router, prefix=f"{settings.API_V1_STR}/copilot")

@app.get("/")
def read_root():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8010, reload=True)
