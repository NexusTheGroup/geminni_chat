"""Logging utilities providing structured JSON output."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from pythonjsonlogger import jsonlogger

from .context import get_celery_task_id, get_correlation_id, get_request_id

_LOGGING_CONFIGURED = False


class _ContextFilter(logging.Filter):
    """Inject request/task identifiers into every log record."""

    def filter(
        self,
        record: logging.LogRecord,
    ) -> bool:  # - short description
        record.request_id = get_request_id()
        record.correlation_id = get_correlation_id()
        record.celery_task_id = get_celery_task_id()
        return True


class _UTCJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter that emits ISO-8601 timestamps in UTC."""

    def formatTime(
        self,
        record: logging.LogRecord,
        datefmt: str | None = None,
    ) -> str:  # - external API
        dt = datetime.fromtimestamp(record.created, tz=UTC)
        return dt.isoformat(timespec="milliseconds")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application-wide structured logging once."""
    global _LOGGING_CONFIGURED  # noqa: PLW0603 - intentional module state
    if _LOGGING_CONFIGURED:
        return

    handler = logging.StreamHandler()
    formatter = _UTCJsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
            "message": "message",
        },
    )
    handler.setFormatter(formatter)
    handler.addFilter(_ContextFilter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    # Ensure libraries inherit the structured output
    logging.captureWarnings(True)

    _LOGGING_CONFIGURED = True


__all__ = ["configure_logging"]
