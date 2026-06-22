import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base, SessionLocal
from .api.endpoints.auth import router as auth_router

# Import all models to register them with SQLAlchemy Base
from .models.user import User
from .models.rbac import Role, Permission, RolePermission, UserRole
from .core.rbac_seed import seed_rbac

# =============================================================================
# Phase 7: Shared observability + security middleware
# =============================================================================
import sys
import os

# Add shared library to path
_shared_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "shared")
if _shared_path not in sys.path:
    sys.path.insert(0, os.path.abspath(_shared_path))

try:
    from observability import setup_observability, add_health_probes
    from security import setup_security
    _SHARED_AVAILABLE = True
except ImportError:
    _SHARED_AVAILABLE = False

# =============================================================================
# Create DB tables & seed RBAC
# =============================================================================
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_rbac(db)
finally:
    db.close()

# =============================================================================
# FastAPI App
# =============================================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Phase 7: Security Middleware (WAF + Rate Limiting + Security Headers) ---
if _SHARED_AVAILABLE:
    setup_security(app, enable_waf=True, enable_security_headers=True, enable_csrf=False)

# --- CORS (restricted to configured origins) ---
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not any(allowed_origins) or allowed_origins == [""]:
    allowed_origins = ["http://localhost:5173", "http://localhost:3000"]  # Dev fallback

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRFToken"],
)

# --- Phase 7: Observability (OTel Tracing + Prometheus Metrics) ---
if _SHARED_AVAILABLE:
    setup_observability(app, service_name="auth-service", service_port=8001)

# --- Routers ---
app.include_router(auth_router, prefix=settings.API_V1_STR)

# --- Phase 7: Health Probes (Kubernetes liveness / readiness) ---
def _db_health_check() -> bool:
    try:
        db = SessionLocal()
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
        return True
    except Exception:
        return False

if _SHARED_AVAILABLE:
    add_health_probes(app, db_check_fn=_db_health_check)
else:
    # Fallback minimal health endpoint
    @app.get("/healthz", include_in_schema=False)
    def healthz():
        return {"status": "alive"}

    @app.get("/readyz", include_in_schema=False)
    def readyz():
        return {"status": "ready"}

    @app.get("/health", include_in_schema=False)
    def health():
        return {"status": "healthy", "service": settings.PROJECT_NAME}


@app.get("/")
def read_root():
    return {"status": "healthy", "service": settings.PROJECT_NAME}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
