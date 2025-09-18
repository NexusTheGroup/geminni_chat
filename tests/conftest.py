from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from nexus_knowledge.db.session import reset_session_factory
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from alembic.config import Config

ROOT_DIR = Path(__file__).resolve().parent.parent


def _alembic_config(database_url: str) -> Config:
    config = Config(str(ROOT_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


@pytest.fixture()
def sqlite_db(
    tmp_path,
    monkeypatch,
) -> Generator[tuple[str, sessionmaker[Session]], None, None]:
    """Provide a temporary SQLite database populated via Alembic migrations."""
    db_path = tmp_path / "nexus_knowledge.db"
    database_url = f"sqlite+pysqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    reset_session_factory()

    config = _alembic_config(database_url)
    command.upgrade(config, "head")

    engine = create_engine(database_url, future=True)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    try:
        yield database_url, session_factory, engine
    finally:
        command.downgrade(config, "base")
        reset_session_factory()
        engine.dispose()
        if db_path.exists():
            os.remove(db_path)
