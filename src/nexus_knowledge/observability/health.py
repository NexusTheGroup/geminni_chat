"""Health and readiness checks for NexusKnowledge services."""

from __future__ import annotations

from typing import Any

import redis
from celery import Celery
from celery.exceptions import CeleryError
from kombu.exceptions import OperationalError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker


def check_database(session_factory: sessionmaker[Session]) -> dict[str, Any]:
    """Perform a lightweight database connectivity check."""
    try:
        session = session_factory()
    except SQLAlchemyError as exc:
        return {"status": "unhealthy", "detail": str(exc)}

    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        return {"status": "unhealthy", "detail": str(exc)}
    finally:
        session.close()

    return {"status": "healthy"}


def check_redis(redis_url: str) -> dict[str, Any]:
    """Ensure the configured Redis broker responds to a ping."""
    try:
        client = redis.Redis.from_url(redis_url, socket_connect_timeout=0.5)
        client.ping()
    except (TimeoutError, redis.RedisError) as exc:
        return {"status": "unhealthy", "detail": str(exc)}
    return {"status": "healthy"}


def check_celery(app: Celery, timeout: float = 1.0) -> dict[str, Any]:
    """Check Celery worker responsiveness via control ping."""
    try:
        ping_response = app.control.ping(timeout=timeout)
    except (OperationalError, CeleryError) as exc:
        return {"status": "unhealthy", "detail": str(exc)}

    if not ping_response:
        return {"status": "degraded", "detail": "no workers responded"}

    return {"status": "healthy", "detail": f"workers={len(ping_response)}"}


def readiness_summary(
    *,
    session_factory: sessionmaker[Session],
    redis_url: str,
    celery_app: Celery,
) -> dict[str, Any]:
    """Compose readiness response aggregating all dependency checks."""
    checks = {
        "database": check_database(session_factory),
        "redis": check_redis(redis_url),
        "celery": check_celery(celery_app),
    }

    overall_status = "ready"
    http_status = 200
    for result in checks.values():
        if result["status"] == "unhealthy":
            overall_status = "unhealthy"
            http_status = 503
            break
        if result["status"] == "degraded" and overall_status != "unhealthy":
            overall_status = "degraded"
            http_status = 503

    return {"status": overall_status, "checks": checks, "http_status": http_status}


def liveness_summary() -> dict[str, Any]:
    """Return the liveness response payload."""
    return {"status": "live"}


__all__ = [
    "check_celery",
    "check_database",
    "check_redis",
    "liveness_summary",
    "readiness_summary",
]
