from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.endpoints.connectors import router as connectors_router

from contextlib import asynccontextmanager
from app.utils.scheduler import sync_engine

# Auto-create database metadata tables on service startup
# Matches the migration schema for in-memory testing and local deployments
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background metadata synchronizer
    sync_engine.start()
    yield
    # Stop background metadata synchronizer
    sync_engine.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Scientific Informatics Platform Data Connector Microservice similar to D360 capabilities.",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for communication with React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(
    connectors_router, 
    prefix=f"{settings.API_V1_STR}/connectors", 
    tags=["Connectors"]
)

@app.get("/", tags=["System"])
def health_check():
    """Health check endpoint confirming service availability."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "timestamp": float(Base.metadata.naming_convention.get("timestamp", 0.0))
    }
