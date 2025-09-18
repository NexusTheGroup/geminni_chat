"""Session helpers for interacting with the project database."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from nexus_knowledge.config import get_settings, reload_settings

_ENGINE: Engine | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None


def get_database_url() -> str:
    """Return the configured database URL from cached settings."""
    return get_settings().database_url


def get_engine(echo: bool = False, url: str | None = None) -> Engine:
    """Create (or return a cached) SQLAlchemy engine for the configured database."""
    global _ENGINE  # noqa: PLW0603
    if url is not None or _ENGINE is None:
        database_url = url or get_database_url()
        _ENGINE = create_engine(database_url, echo=echo, future=True)
    return _ENGINE


def get_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Return a session factory bound to the configured engine."""
    global _SESSION_FACTORY  # noqa: PLW0603
    if engine is not None:
        _SESSION_FACTORY = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
        return _SESSION_FACTORY

    if _SESSION_FACTORY is None:
        engine = get_engine()
        _SESSION_FACTORY = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
    return _SESSION_FACTORY


@contextmanager
def session_scope(
    factory: sessionmaker[Session] | None = None,
) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session_factory = factory or get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover - re-raised for calling context to handle
        session.rollback()
        raise
    finally:
        session.close()


def reset_session_factory() -> None:
    """Reset cached engine/session factory (useful for tests)."""
    global _ENGINE, _SESSION_FACTORY  # noqa: PLW0603
    _ENGINE = None
    _SESSION_FACTORY = None
    reload_settings()


def get_session_dependency() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for FastAPI dependencies."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()
