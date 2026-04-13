"""
Synchronous SQLAlchemy engine for use inside Celery workers.

Celery tasks run in a standard synchronous context, so we maintain
a separate sync engine alongside the async one used by FastAPI.
Both point to the same database — only the driver differs:
  - FastAPI  → asyncpg  (async)
  - Celery   → psycopg2 (sync)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Replace asyncpg driver with psycopg2 for sync access
_sync_url = settings.database_url.replace(
    "postgresql+asyncpg://", "postgresql+psycopg2://"
)

sync_engine = create_engine(
    _sync_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SyncSessionFactory: sessionmaker[Session] = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
