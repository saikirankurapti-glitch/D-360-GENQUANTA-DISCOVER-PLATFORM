import os

class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Discover Auth Service"
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SUPER_SECRET_SCIENTIFIC_PLATFORM_KEY_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Database Settings – PostgreSQL (Phase 8)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/genquantaa_auth")

settings = Settings()
