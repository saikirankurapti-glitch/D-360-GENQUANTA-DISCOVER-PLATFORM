# app/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints.chemistry import router as chemistry_router

# Perform table creation (for SQLite local development / test suites)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-performance cheminformatics query, search, and SAR microservice utilizing RDKit.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for cross-service calls and frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include endpoint routes
app.include_router(chemistry_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "api_version": "1.0.0"
    }

if __name__ == "__main__":
    # Run locally on port 8004
    uvicorn.run("app.main:app", host="0.0.0.0", port=8004, reload=True)
