import os
import sys
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AnalytiX Data Connector Service"
    
    # Database connection URL – PostgreSQL (Phase 8)
    # SQLite fallback for local test execution
    DATABASE_URL: str = "sqlite:///:memory:" if "pytest" in sys.modules else os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/genquantaa_connector"
    )
    
    # Redis configuration for cache and task queues
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Key used for encrypting data source connection credentials (AES-256)
    # Stored in env, fall back to a default key for development
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "351F6FEE44C2BD56A11D36982DB5F11F351F6FEE44C2BD56A11D36982DB5F11F")

    model_config = ConfigDict(case_sensitive=True)

settings = Settings()
