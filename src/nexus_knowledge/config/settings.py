"""Application configuration loader and validation helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

AppEnv = Literal["local", "test", "prod"]

_ALLOWED_LOG_LEVELS = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
_DEFAULT_SECRET_PLACEHOLDER = os.getenv(
    "GEMINNI_SECRET_PLACEHOLDER",
    "CHANGE_ME_IN_PRODUCTION",
)


class ConfigurationError(RuntimeError):
    """Raised when configuration validation fails."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


class Settings(BaseSettings):
    """Centralised application settings with validation and defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: AppEnv = Field("local", alias="APP_ENV")
    database_url: str = Field(..., alias="DATABASE_URL")
    redis_url: str = Field(..., alias="REDIS_URL")
    mlflow_tracking_uri: str = Field(..., alias="MLFLOW_TRACKING_URI")
    secret_key: SecretStr = Field(..., alias="SECRET_KEY")

    log_level: str = Field("INFO", alias="LOG_LEVEL")
    api_root: str = Field("/api/v1", alias="API_ROOT")
    benchmark_thresholds_path: str | None = Field(
        default=None,
        alias="BENCHMARK_THRESHOLDS_PATH",
    )

    celery_worker_concurrency: int = Field(2, alias="CELERY_WORKER_CONCURRENCY", ge=1)
    celery_prefetch_multiplier: int = Field(1, alias="CELERY_PREFETCH_MULTIPLIER", ge=1)
    celery_task_soft_time_limit: int = Field(
        600,
        alias="CELERY_TASK_SOFT_TIME_LIMIT",
        ge=60,
    )
    celery_task_time_limit: int = Field(900, alias="CELERY_TASK_TIME_LIMIT", ge=60)
    celery_task_retry_delay: int = Field(5, alias="CELERY_TASK_RETRY_DELAY", ge=0)
    celery_task_retry_backoff_max: int = Field(
        600,
        alias="CELERY_TASK_RETRY_BACKOFF_MAX",
        ge=0,
    )
    celery_max_tasks_per_child: int = Field(
        200,
        alias="CELERY_MAX_TASKS_PER_CHILD",
        ge=1,
    )
    celery_broker_pool_limit: int = Field(10, alias="CELERY_BROKER_POOL_LIMIT", ge=0)
    celery_broker_connection_timeout: float = Field(
        5.0,
        alias="CELERY_BROKER_CONN_TIMEOUT",
        ge=0,
    )

    @field_validator("log_level")
    @classmethod
    def _normalise_log_level(cls, value: str) -> str:
        upper = value.upper()
        if upper not in _ALLOWED_LOG_LEVELS:
            raise ValueError(
                f"LOG_LEVEL must be one of {sorted(_ALLOWED_LOG_LEVELS)}, got '{value}'.",
            )
        return upper

    @field_validator("api_root")
    @classmethod
    def _validate_api_root(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("API_ROOT must start with '/'.")
        return value.rstrip("/") or "/"

    @model_validator(mode="after")
    def _validate_urls(self) -> Settings:  # pragma: no cover - simple helpers
        url_fields = {
            "DATABASE_URL": self.database_url,
            "REDIS_URL": self.redis_url,
            "MLFLOW_TRACKING_URI": self.mlflow_tracking_uri,
        }
        for label, raw in url_fields.items():
            try:
                make_url(raw)
            except ArgumentError as exc:  # pragma: no cover - edge formatting cases
                raise ValueError(f"{label} is invalid: {exc}") from exc
        return self

    def validate_for_environment(self) -> None:
        """Perform environment-specific validation (e.g. production hardening)."""
        errors: list[str] = []

        secret_value = self.secret_key.get_secret_value()
        if self.app_env == "prod":
            if len(secret_value) < 32 or secret_value == _DEFAULT_SECRET_PLACEHOLDER:
                errors.append(
                    "SECRET_KEY must be at least 32 characters and customised in production.",
                )
            if self.database_url.startswith("sqlite"):
                errors.append("DATABASE_URL cannot use SQLite in production.")
            if self.log_level == "DEBUG":
                errors.append("LOG_LEVEL must not be DEBUG in production.")
        if errors:
            raise ConfigurationError(errors)


@lru_cache(maxsize=1)
def _build_settings() -> Settings:
    try:
        settings = Settings()
    except ValidationError as exc:
        messages = [
            f"{'.'.join(str(loc) for loc in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        ]
        raise ConfigurationError(messages) from exc

    settings.validate_for_environment()
    return settings


def get_settings() -> Settings:
    """Return cached settings instance."""
    return _build_settings()


def reload_settings() -> Settings:
    """Clear cache and rebuild settings (useful for tests/CLI)."""
    clear_settings_cache()
    return get_settings()


def clear_settings_cache() -> None:
    """Clear cached settings without reloading."""
    _build_settings.cache_clear()


__all__ = [
    "ConfigurationError",
    "Settings",
    "clear_settings_cache",
    "get_settings",
    "reload_settings",
]
