"""Async SQLAlchemy configuration for AnalytiX (Supabase)"""
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Connection URL
# ---------------------------------------------------------------------------
# Use DATABASE_URL_ASYNC (postgresql+asyncpg://...) if set,
# otherwise fall back to DATABASE_URL and swap the scheme automatically.

_raw_url = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")
if not _raw_url:
    raise RuntimeError(
        "Neither DATABASE_URL_ASYNC nor DATABASE_URL is set. "
        "Copy backend/.env.example → backend/.env and fill in your Supabase credentials."
    )

# Ensure the asyncpg driver prefix is present
if _raw_url.startswith("postgresql://"):
    _raw_url = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

DATABASE_URL = _raw_url

# ---------------------------------------------------------------------------
# Async Engine (connection‑pool ready for Supabase Pooler / PgBouncer)
# ---------------------------------------------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("ENVIRONMENT", "production") == "development",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,       # recycle connections every 5 min (Supabase best practice)
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ---------------------------------------------------------------------------
# Base class for all SQLAlchemy models
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass

# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------
async def get_async_db():
    """Yields an async session, commits on success, rolls back on error."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
