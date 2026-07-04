"""Database engine + session management.

Reads DATABASE_URL from the environment (set it to your Neon connection
string). The engine is created lazily so the app boots fine without a
database — gamification endpoints raise a clear error instead of crashing
the whole service.

Neon connection strings look like:
    postgresql://user:pass@ep-xxx.ap-southeast-1.aws.neon.tech/dbname?sslmode=require

We rewrite the scheme to use the psycopg (v3) driver automatically.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Engine | None = None
_SessionFactory: sessionmaker[Session] | None = None


def _normalize_url(url: str) -> str:
    """Rewrite a plain Postgres URL to use the psycopg v3 driver."""
    if url.startswith("postgresql+"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


def is_db_configured() -> bool:
    """True if DATABASE_URL is set (gamification persistence available)."""
    return bool(os.getenv("DATABASE_URL", "").strip())


def get_engine() -> Engine:
    """Return the lazily-created SQLAlchemy engine. Raises if DATABASE_URL unset."""
    global _engine, _SessionFactory
    if _engine is None:
        url = os.getenv("DATABASE_URL", "").strip()
        if not url:
            raise RuntimeError(
                "DATABASE_URL is not set. Gamification features require a "
                "Postgres connection (see backend/app/db/README.md)."
            )
        _engine = create_engine(
            _normalize_url(url),
            pool_pre_ping=True,  # validate connections (Neon scales to zero)
            pool_size=5,
            max_overflow=5,
        )
        _SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


@contextmanager
def get_session() -> Iterator[Session]:
    """Context-managed session: commits on success, rolls back on error."""
    global _SessionFactory
    if _SessionFactory is None:
        get_engine()
    assert _SessionFactory is not None
    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
