from __future__ import annotations

import pytest


@pytest.mark.no_celery_mock
def test_celery_configuration_defaults(monkeypatch) -> None:
    monkeypatch.setenv("CELERY_WORKER_CONCURRENCY", "3")
    monkeypatch.setenv("CELERY_PREFETCH_MULTIPLIER", "2")
    monkeypatch.setenv("CELERY_TASK_SOFT_TIME_LIMIT", "700")
    monkeypatch.setenv("CELERY_TASK_TIME_LIMIT", "800")
    monkeypatch.setenv("CELERY_TASK_RETRY_DELAY", "6")
    monkeypatch.setenv("CELERY_TASK_RETRY_BACKOFF_MAX", "700")
    monkeypatch.setenv("CELERY_MAX_TASKS_PER_CHILD", "201")
    monkeypatch.setenv("CELERY_BROKER_POOL_LIMIT", "11")
    monkeypatch.setenv("CELERY_BROKER_CONN_TIMEOUT", "6")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    monkeypatch.setenv("SECRET_KEY", "z" * 40)

    import importlib

    from nexus_knowledge.config import clear_settings_cache, reload_settings

    clear_settings_cache()
    tasks_module = importlib.import_module("nexus_knowledge.tasks")
    importlib.reload(tasks_module)

    settings = reload_settings()
    celery_app = tasks_module.celery_app
    assert settings.celery_worker_concurrency == 3
    assert settings.celery_prefetch_multiplier == 2

    assert (
        celery_app.conf.worker_prefetch_multiplier
        == settings.celery_prefetch_multiplier
    )
    assert celery_app.conf.task_soft_time_limit == settings.celery_task_soft_time_limit
    assert celery_app.conf.task_time_limit == settings.celery_task_time_limit
    assert celery_app.conf.task_default_retry_delay == settings.celery_task_retry_delay
    assert (
        celery_app.conf.task_default_retry_backoff_max
        == settings.celery_task_retry_backoff_max
    )
