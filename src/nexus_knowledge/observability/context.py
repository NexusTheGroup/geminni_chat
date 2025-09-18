"""Context variable helpers for observability metadata."""

from __future__ import annotations

from contextvars import ContextVar, Token

_RequestIdVar: ContextVar[str | None] = ContextVar("nexus_request_id", default=None)
_CorrelationIdVar: ContextVar[str | None] = ContextVar(
    "nexus_correlation_id",
    default=None,
)
_CeleryTaskIdVar: ContextVar[str | None] = ContextVar(
    "nexus_celery_task_id",
    default=None,
)


def get_request_id() -> str | None:
    """Return the current request identifier, if any."""
    return _RequestIdVar.get()


def get_correlation_id() -> str | None:
    """Return the current correlation identifier, if any."""
    return _CorrelationIdVar.get()


def get_celery_task_id() -> str | None:
    """Return the current Celery task identifier, if any."""
    return _CeleryTaskIdVar.get()


def push_request_context(
    request_id: str,
    correlation_id: str | None = None,
) -> tuple[Token[str | None], Token[str | None]]:
    """Store request/correlation identifiers and return tokens for reset."""
    correlation = correlation_id or request_id
    request_token = _RequestIdVar.set(request_id)
    correlation_token = _CorrelationIdVar.set(correlation)
    return request_token, correlation_token


def pop_request_context(
    request_token: Token[str | None],
    correlation_token: Token[str | None],
) -> None:
    """Reset request/correlation identifiers using provided context tokens."""
    _RequestIdVar.reset(request_token)
    _CorrelationIdVar.reset(correlation_token)


def push_celery_context(
    task_id: str,
    correlation_id: str | None = None,
) -> tuple[Token[str | None], Token[str | None] | None]:
    """Store Celery task context and optionally override correlation id."""
    task_token = _CeleryTaskIdVar.set(task_id)
    correlation_token: Token[str | None] | None = None
    if correlation_id is not None:
        correlation_token = _CorrelationIdVar.set(correlation_id)
    return task_token, correlation_token


def pop_celery_context(
    task_token: Token[str | None],
    correlation_token: Token[str | None] | None,
) -> None:
    """Reset Celery task context using the provided tokens."""
    _CeleryTaskIdVar.reset(task_token)
    if correlation_token is not None:
        _CorrelationIdVar.reset(correlation_token)


__all__ = [
    "get_request_id",
    "get_correlation_id",
    "get_celery_task_id",
    "push_request_context",
    "pop_request_context",
    "push_celery_context",
    "pop_celery_context",
]
