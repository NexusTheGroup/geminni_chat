from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from nexus_knowledge.config import clear_settings_cache
from nexus_knowledge.db.session import reset_session_factory
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from alembic.config import Config

ROOT_DIR = Path(__file__).resolve().parent.parent

# Set default environment variables for tests
os.environ.setdefault("DATABASE_URL", "sqlite:///test_nexus_knowledge.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("MLFLOW_TRACKING_URI", f"file://{ROOT_DIR}/mlruns")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-purposes-only")
os.environ.setdefault("APP_ENV", "test")
# Note: LOG_LEVEL is intentionally not set here to allow individual tests to control it


def _alembic_config(database_url: str) -> Config:
    config = Config(str(ROOT_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


class MockAsyncResult:
    """Mock AsyncResult for Celery task testing."""

    def __init__(self, task_id: str = "test-task-id"):
        self.id = task_id
        self.state = "PENDING"
        self.result = None

    def get(self, timeout=None):
        return self.result

    def ready(self):
        return self.state in ("SUCCESS", "FAILURE")

    def successful(self):
        return self.state == "SUCCESS"


@pytest.fixture(autouse=True)
def mock_celery_tasks(request, monkeypatch):
    """Automatically mock Celery task methods to avoid requiring a real broker/worker."""
    # Skip mocking for tests that need real Celery configuration
    if hasattr(request, "node") and "no_celery_mock" in request.node.keywords:
        return {}

    task_calls = []

    def mock_delay(*args, **kwargs):
        task_calls.append(("delay", args, kwargs))
        result = MockAsyncResult()
        # Set task id for tests that check it
        result.id = f"task-{len(task_calls)}"
        return result

    def mock_apply_async(*args, **kwargs):
        task_calls.append(("apply_async", args, kwargs))
        result = MockAsyncResult()
        result.id = f"task-{len(task_calls)}"
        return result

    # Create a mock task that has delay and apply_async methods
    def create_mock_task():
        mock_task = MagicMock()
        mock_task.delay = mock_delay
        mock_task.apply_async = mock_apply_async
        return mock_task

    # Mock Celery app initialization to avoid connection errors
    def mock_celery_init(*args, **kwargs):
        mock_app = MagicMock()

        # Mock the task decorator
        def mock_task_decorator(*decorator_args, **decorator_kwargs):
            def wrapper(func):
                mock_task_obj = create_mock_task()
                # Store original function for potential direct calls
                mock_task_obj._original_func = func
                # Add apply method for synchronous execution
                mock_task_obj.apply = lambda args=(), kwargs={}: MockAsyncResult()
                return mock_task_obj

            # Handle both @task and @task() usage
            if (
                len(decorator_args) == 1
                and callable(decorator_args[0])
                and not decorator_kwargs
            ):
                return wrapper(decorator_args[0])
            else:
                return wrapper

        mock_app.task = mock_task_decorator
        return mock_app

    monkeypatch.setattr("celery.Celery", mock_celery_init)

    # Also mock at module level for imports that happen during test
    try:
        import nexus_knowledge.tasks

        # Replace task methods with mocks
        if hasattr(nexus_knowledge.tasks, "normalize_raw_data_task"):
            monkeypatch.setattr(
                nexus_knowledge.tasks.normalize_raw_data_task,
                "delay",
                mock_delay,
            )
            monkeypatch.setattr(
                nexus_knowledge.tasks.normalize_raw_data_task,
                "apply_async",
                mock_apply_async,
            )
        if hasattr(nexus_knowledge.tasks, "analyze_raw_data_task"):
            monkeypatch.setattr(
                nexus_knowledge.tasks.analyze_raw_data_task,
                "delay",
                mock_delay,
            )
            monkeypatch.setattr(
                nexus_knowledge.tasks.analyze_raw_data_task,
                "apply_async",
                mock_apply_async,
            )
        if hasattr(nexus_knowledge.tasks, "persist_feedback"):
            monkeypatch.setattr(
                nexus_knowledge.tasks.persist_feedback,
                "delay",
                mock_delay,
            )
            monkeypatch.setattr(
                nexus_knowledge.tasks.persist_feedback,
                "apply_async",
                mock_apply_async,
            )
        if hasattr(nexus_knowledge.tasks, "export_obsidian_task"):
            monkeypatch.setattr(
                nexus_knowledge.tasks.export_obsidian_task,
                "delay",
                mock_delay,
            )
            monkeypatch.setattr(
                nexus_knowledge.tasks.export_obsidian_task,
                "apply_async",
                mock_apply_async,
            )
        if hasattr(nexus_knowledge.tasks, "generate_correlation_candidates_task"):
            monkeypatch.setattr(
                nexus_knowledge.tasks.generate_correlation_candidates_task,
                "delay",
                mock_delay,
            )
            monkeypatch.setattr(
                nexus_knowledge.tasks.generate_correlation_candidates_task,
                "apply_async",
                mock_apply_async,
            )
        if hasattr(nexus_knowledge.tasks, "fuse_correlation_candidates_task"):
            monkeypatch.setattr(
                nexus_knowledge.tasks.fuse_correlation_candidates_task,
                "delay",
                mock_delay,
            )
            monkeypatch.setattr(
                nexus_knowledge.tasks.fuse_correlation_candidates_task,
                "apply_async",
                mock_apply_async,
            )
    except ImportError:
        # Tasks module might not be importable in test environment without proper setup
        pass

    # Return the mock functions so tests can use them
    return {
        "calls": task_calls,
        "mock_delay": mock_delay,
        "mock_apply_async": mock_apply_async,
    }


@pytest.fixture(autouse=True)
def clean_mlflow_context():
    """Ensure MLflow runs are properly cleaned up between tests."""
    import mlflow

    # End any active runs before starting test
    try:
        while mlflow.active_run():
            mlflow.end_run()
    except Exception:
        pass

    yield

    # Clean up after test
    try:
        while mlflow.active_run():
            mlflow.end_run()
    except Exception:
        pass


@pytest.fixture()
def sqlite_db(
    tmp_path,
    monkeypatch,
) -> Generator[tuple[str, sessionmaker[Session]], None, None]:
    """Provide a temporary SQLite database populated via Alembic migrations."""
    db_path = tmp_path / "nexus_knowledge.db"
    database_url = f"sqlite+pysqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"file://{tmp_path}/mlruns")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-12345678901234567890")
    reset_session_factory()
    clear_settings_cache()

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
