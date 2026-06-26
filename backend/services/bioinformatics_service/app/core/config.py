import os

class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AnalytiX Bioinformatics Service"
    # Database Settings – PostgreSQL (Phase 8)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/genquantaa_bioinfo")

settings = Settings()
