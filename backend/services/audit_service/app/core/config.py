import os

class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AnalytiX Audit Service"
    
    # Audit Service Specific Settings
    # API Secret Key for validation/submission auth from other services
    AUDIT_API_SECRET: str = os.getenv("AUDIT_API_SECRET", "AnalytiX_AUDIT_INTERNAL_API_SECRET_2026")
    
    # Database Settings – PostgreSQL (Phase 8)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/genquantaa_audit")

settings = Settings()
