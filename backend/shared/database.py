# backend/shared/database.py
# =============================================================================
# GENQUANTAA Discover – Shared PostgreSQL Database Module
# Phase 8: Unified database engine factory with connection pooling,
# async support, transaction management, and HA-ready configuration.
# =============================================================================

from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool


def create_pg_engine(
    database_url: str,
    *,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_pre_ping: bool = True,
    pool_recycle: int = 1800,
    echo: bool = False,
):
    """
    Create a production-grade PostgreSQL engine with connection pooling.

    Args:
        database_url: PostgreSQL connection string
        pool_size: Number of persistent connections in the pool
        max_overflow: Max temporary connections above pool_size
        pool_pre_ping: Verify connections before use (detects stale connections)
        pool_recycle: Seconds before a connection is recycled (prevents server-side timeouts)
        echo: Enable SQL statement logging
    """
    # Support SQLite for test environments (in-memory or file-based)
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=echo,
        )

    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        pool_recycle=pool_recycle,
        echo=echo,
        # PostgreSQL-specific optimizations
        connect_args={
            "options": "-c statement_timeout=30000",  # 30s query timeout
        },
    )


def create_session_factory(engine):
    """Create a sessionmaker bound to the given engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def transaction_scope(session_factory):
    """
    Provide a transactional scope around a series of operations.

    Usage:
        with transaction_scope(SessionLocal) as session:
            session.add(obj)
            # auto-commits on success, auto-rollbacks on exception
    """
    session: Session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_db_health(engine) -> bool:
    """
    Health check: verify the database is reachable.
    Returns True if a simple query succeeds, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
