import os
import sys
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Discover Cheminformatics Service"
    
    # Database configuration
    # Defaulting to PostgreSQL for production RDKit Cartridge support
    # Automatically falls back to in-memory SQLite if running unit tests
    DATABASE_URL: str = "sqlite:///:memory:" if "pytest" in sys.modules else os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/cheminformatics"
    )
    
    # Chemistry settings
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.7  # Tanimoto similarity threshold
    MAX_SEARCH_RESULTS: int = 100
    
    model_config = ConfigDict(case_sensitive=True)

settings = Settings()

