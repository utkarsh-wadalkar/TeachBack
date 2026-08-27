"""Database engine and session management."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import BACKEND_DIR, settings


def _resolve_database_url(url: str) -> str:
    """Anchor relative SQLite paths to backend/ so the database location is
    independent of the working directory the server was started from."""
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return url
    path = url[len(prefix) :]
    if not path or path.startswith(":memory:") or path.startswith("/"):
        return url
    return f"{prefix}{(BACKEND_DIR / path).as_posix()}"


# SQLite needs check_same_thread disabled for FastAPI's threadpool; other
# databases take no special connect args.
_connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    _resolve_database_url(settings.database_url),
    connect_args=_connect_args,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a database session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
