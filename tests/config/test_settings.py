from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from nexus_knowledge.config import (
    ConfigurationError,
    clear_settings_cache,
    get_settings,
    reload_settings,
)

BASE_ENV = {
    "APP_ENV": "local",
    "DATABASE_URL": "sqlite+pysqlite:///:memory:",
    "REDIS_URL": "redis://localhost:6379/0",
    "MLFLOW_TRACKING_URI": "http://localhost:5000",
    "SECRET_KEY": "x" * 40,
}


@pytest.fixture(autouse=True)
def _reset_settings() -> None:
    clear_settings_cache()
    yield
    clear_settings_cache()


def _set_base_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)


def test_settings_load_with_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_base_env(monkeypatch)
    settings = reload_settings()
    assert settings.app_env == "local"
    assert settings.database_url == BASE_ENV["DATABASE_URL"]
    assert settings.log_level == "INFO"
    assert settings.celery_worker_concurrency == 2


def test_missing_required_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    env = {k: v for k, v in BASE_ENV.items() if k != "SECRET_KEY"}
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("SECRET_KEY", raising=False)

    clear_settings_cache()
    with pytest.raises(ConfigurationError) as exc:
        get_settings()
    assert any("SECRET_KEY" in message for message in exc.value.errors)


def test_prod_requires_strong_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_base_env(monkeypatch)
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("SECRET_KEY", "weak")

    clear_settings_cache()
    with pytest.raises(ConfigurationError) as exc:
        get_settings()
    assert "SECRET_KEY" in " ".join(exc.value.errors)


def test_reload_settings_reflects_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_base_env(monkeypatch)
    clear_settings_cache()
    first = get_settings()
    assert first.secret_key.get_secret_value().startswith("x")

    monkeypatch.setenv("SECRET_KEY", "y" * 40)
    updated = reload_settings()
    assert updated.secret_key.get_secret_value().startswith("y")


def test_validate_cli_reports_success(monkeypatch: pytest.MonkeyPatch) -> None:
    env = os.environ.copy()
    env.update(BASE_ENV)
    env["SECRET_KEY"] = "z" * 40

    result = subprocess.run(
        [sys.executable, "scripts/config/validate.py"],
        env=env,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[2],
        check=False,
    )
    assert result.returncode == 0
    assert "Configuration OK" in result.stdout


def test_validate_cli_reports_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    env = os.environ.copy()
    env.update(BASE_ENV)
    env.pop("DATABASE_URL", None)

    result = subprocess.run(
        [sys.executable, "scripts/config/validate.py"],
        env=env,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[2],
        check=False,
    )
    assert result.returncode == 1
    assert "DATABASE_URL" in result.stderr


def test_config_migration_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    env = os.environ.copy()
    env.update(BASE_ENV)

    result = subprocess.run(
        [sys.executable, "scripts/config/migrate.py"],
        env=env,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[2],
        check=False,
    )
    assert result.returncode == 0
    assert "Configuration schema check passed" in result.stdout
