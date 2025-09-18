"""Prometheus metrics helpers for API and Celery instrumentation."""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNTER = Counter(
    "nexus_api_requests_total",
    "Total number of API requests processed",
    labelnames=("method", "route", "status"),
)
REQUEST_LATENCY = Histogram(
    "nexus_api_request_duration_seconds",
    "API request latency in seconds",
    labelnames=("method", "route"),
    buckets=(0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
REQUEST_ERRORS = Counter(
    "nexus_api_errors_total",
    "API errors grouped by route and error type",
    labelnames=("method", "route", "error_type"),
)
TASK_COUNTER = Counter(
    "nexus_celery_task_total",
    "Celery task lifecycle counter",
    labelnames=("task_name", "status"),
)
TASK_DURATION = Histogram(
    "nexus_celery_task_duration_seconds",
    "Celery task duration in seconds",
    labelnames=("task_name",),
    buckets=(0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60),
)
TASK_FAILURES = Counter(
    "nexus_celery_task_failures_total",
    "Celery task failures grouped by task and exception type",
    labelnames=("task_name", "exception"),
)


def _normalise_route(route: str) -> str:
    return route or "unknown"


def observe_api_request(
    method: str,
    route: str,
    status_code: int,
    duration_seconds: float,
) -> None:
    """Record API request metrics for Prometheus."""
    method_name = method.upper()
    route_name = _normalise_route(route)
    REQUEST_COUNTER.labels(
        method=method_name,
        route=route_name,
        status=str(status_code),
    ).inc()
    REQUEST_LATENCY.labels(method=method_name, route=route_name).observe(
        duration_seconds,
    )


def observe_api_error(method: str, route: str, error_type: str) -> None:
    """Record API error occurrences."""
    REQUEST_ERRORS.labels(
        method=method.upper(),
        route=_normalise_route(route),
        error_type=error_type,
    ).inc()


@contextmanager
def track_task_execution(task_name: str) -> Iterator[None]:
    """Context manager that instruments Celery task execution metrics."""
    TASK_COUNTER.labels(task_name=task_name, status="started").inc()
    start = time.perf_counter()
    try:
        yield
    except Exception as exc:
        TASK_COUNTER.labels(task_name=task_name, status="failed").inc()
        TASK_FAILURES.labels(
            task_name=task_name,
            exception=exc.__class__.__name__,
        ).inc()
        raise
    else:
        TASK_COUNTER.labels(task_name=task_name, status="succeeded").inc()
    finally:
        duration = time.perf_counter() - start
        TASK_DURATION.labels(task_name=task_name).observe(duration)


def observe_task_failure(task_name: str, exception_type: str) -> None:
    """Record a Celery task failure that occurs outside the tracked context."""
    TASK_COUNTER.labels(task_name=task_name, status="failed").inc()
    TASK_FAILURES.labels(task_name=task_name, exception=exception_type).inc()


def collect_metrics() -> bytes:
    """Return the Prometheus metrics exposition payload."""
    return generate_latest()


__all__ = [
    "CONTENT_TYPE_LATEST",
    "collect_metrics",
    "observe_api_request",
    "observe_api_error",
    "track_task_execution",
    "observe_task_failure",
]
