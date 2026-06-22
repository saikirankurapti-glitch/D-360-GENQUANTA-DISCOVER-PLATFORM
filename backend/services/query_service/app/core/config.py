import os

class Settings:
    PROJECT_NAME: str = "Query Service"
    API_V1_STR: str = "/api/v1"
    # Database Settings – PostgreSQL (Phase 8)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/genquantaa_query")

settings = Settings()
