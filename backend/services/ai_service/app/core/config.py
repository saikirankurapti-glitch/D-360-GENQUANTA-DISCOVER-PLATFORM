import os

class Settings:
    PROJECT_NAME: str = "AI Copilot Service"
    API_V1_STR: str = "/api/v1"
    # Database Settings – PostgreSQL (Phase 8)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/genquantaa_ai")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

settings = Settings()
