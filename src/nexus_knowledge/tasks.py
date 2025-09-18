"""Celery task definitions with observability instrumentation."""

from __future__ import annotations

import logging
import uuid
from typing import Any

import mlflow
from celery import Celery

from nexus_knowledge.analysis.pipeline import run_analysis_for_raw_data
from nexus_knowledge.config import get_settings
from nexus_knowledge.correlation import generate_candidates_for_raw
from nexus_knowledge.correlation.pipeline import fuse_candidates_for_raw
from nexus_knowledge.db.repository import create_user_feedback
from nexus_knowledge.db.session import session_scope
from nexus_knowledge.experiment_tracking import log_task_artifact, mlflow_task_run
from nexus_knowledge.export import export_to_obsidian
from nexus_knowledge.ingestion.service import normalize_raw_data
from nexus_knowledge.observability import (
    configure_logging,
    pop_celery_context,
    push_celery_context,
    track_task_execution,
)

settings = get_settings()

configure_logging()

celery_app = Celery(
    "nexus_knowledge_tasks",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.update(
    worker_prefetch_multiplier=settings.celery_prefetch_multiplier,
    task_acks_late=True,
    task_default_queue="default",
    task_default_retry_delay=settings.celery_task_retry_delay,
    task_default_retry_backoff=True,
    task_default_retry_backoff_max=settings.celery_task_retry_backoff_max,
    task_default_retry_jitter=True,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    task_time_limit=settings.celery_task_time_limit,
    worker_max_tasks_per_child=settings.celery_max_tasks_per_child,
    worker_concurrency=settings.celery_worker_concurrency,
    broker_pool_limit=settings.celery_broker_pool_limit,
    broker_connection_timeout=settings.celery_broker_connection_timeout,
)
logger = logging.getLogger(__name__)


def _bind_task_context(
    task: Any,
    correlation_id: str | None = None,
) -> tuple[str, Any, Any | None]:
    task_id = (
        getattr(getattr(task, "request", None), "id", None)
        or f"task-{uuid.uuid4().hex}"
    )
    task_token, correlation_token = push_celery_context(task_id, correlation_id)
    return task_id, task_token, correlation_token


@celery_app.task(bind=True)
def persist_feedback(
    self,
    feedback_id: str,
    payload: dict[str, Any],
    *,
    correlation_id: str | None = None,
) -> str:
    """Persist user feedback asynchronously to keep the API responsive."""
    task_name = self.name or "nexus_knowledge.tasks.persist_feedback"
    task_id, task_token, correlation_token = _bind_task_context(self, correlation_id)
    logger.info(
        "task.started",
        extra={"task_name": task_name, "task_id": task_id, "feedback_id": feedback_id},
    )
    try:
        with track_task_execution(task_name), session_scope() as session:
            create_user_feedback(
                session,
                feedback_id=uuid.UUID(feedback_id),
                feedback_type=payload["feedback_type"],
                message=payload["message"],
                user_id=(
                    uuid.UUID(payload["user_id"]) if payload.get("user_id") else None
                ),
            )
    except Exception:
        logger.exception(
            "task.failed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        raise
    else:
        logger.info(
            "task.completed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        return feedback_id
    finally:
        pop_celery_context(task_token, correlation_token)


@celery_app.task(bind=True)
def normalize_raw_data_task(
    self,
    raw_data_id: str,
    *,
    correlation_id: str | None = None,
) -> str:
    """Normalize the stored raw payload into conversation turns."""
    task_name = self.name or "nexus_knowledge.tasks.normalize_raw_data_task"
    task_id, task_token, correlation_token = _bind_task_context(self, correlation_id)
    logger.info(
        "task.started",
        extra={"task_name": task_name, "task_id": task_id, "raw_data_id": raw_data_id},
    )
    try:
        raw_uuid = uuid.UUID(raw_data_id)
        with (
            track_task_execution(task_name),
            mlflow_task_run(
                task_name,
                raw_data_id=raw_uuid,
                correlation_id=correlation_id,
            ),
        ):
            with session_scope() as session:
                processed = normalize_raw_data(session, raw_uuid)
            mlflow.log_metric("turns_normalized", processed)
    except Exception:
        logger.exception(
            "task.failed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        raise
    else:
        logger.info(
            "task.completed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        return raw_data_id
    finally:
        pop_celery_context(task_token, correlation_token)


@celery_app.task(bind=True)
def analyze_raw_data_task(
    self,
    raw_data_id: str,
    *,
    correlation_id: str | None = None,
) -> str:
    """Run sentiment analysis on normalized conversation turns."""
    task_name = self.name or "nexus_knowledge.tasks.analyze_raw_data_task"
    task_id, task_token, correlation_token = _bind_task_context(self, correlation_id)
    logger.info(
        "task.started",
        extra={"task_name": task_name, "task_id": task_id, "raw_data_id": raw_data_id},
    )
    try:
        raw_uuid = uuid.UUID(raw_data_id)
        with (
            track_task_execution(task_name),
            mlflow_task_run(
                task_name,
                raw_data_id=raw_uuid,
                correlation_id=correlation_id,
                params={"pipeline": "heuristic_sentiment"},
            ),
        ):
            with session_scope() as session:
                processed = run_analysis_for_raw_data(session, raw_uuid)
            mlflow.log_metric("turns_analyzed", processed)
    except Exception:
        logger.exception(
            "task.failed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        raise
    else:
        logger.info(
            "task.completed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        return raw_data_id
    finally:
        pop_celery_context(task_token, correlation_token)


@celery_app.task(bind=True)
def generate_correlation_candidates_task(
    self,
    raw_data_id: str,
    *,
    correlation_id: str | None = None,
) -> str:
    """Generate correlation candidates for a raw payload."""
    task_name = (
        self.name or "nexus_knowledge.tasks.generate_correlation_candidates_task"
    )
    task_id, task_token, correlation_token = _bind_task_context(self, correlation_id)
    logger.info(
        "task.started",
        extra={"task_name": task_name, "task_id": task_id, "raw_data_id": raw_data_id},
    )
    try:
        raw_uuid = uuid.UUID(raw_data_id)
        with (
            track_task_execution(task_name),
            mlflow_task_run(
                task_name,
                raw_data_id=raw_uuid,
                correlation_id=correlation_id,
                params={"pipeline": "correlation_generation"},
            ),
        ):
            with session_scope() as session:
                generated = generate_candidates_for_raw(session, raw_uuid)
            mlflow.log_metric("candidates_generated", generated)
    except Exception:
        logger.exception(
            "task.failed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        raise
    else:
        logger.info(
            "task.completed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        return raw_data_id
    finally:
        pop_celery_context(task_token, correlation_token)


@celery_app.task(bind=True)
def fuse_correlation_candidates_task(
    self,
    raw_data_id: str,
    *,
    correlation_id: str | None = None,
) -> str:
    """Fuse correlation candidates into relationships."""
    task_name = self.name or "nexus_knowledge.tasks.fuse_correlation_candidates_task"
    task_id, task_token, correlation_token = _bind_task_context(self, correlation_id)
    logger.info(
        "task.started",
        extra={"task_name": task_name, "task_id": task_id, "raw_data_id": raw_data_id},
    )
    try:
        raw_uuid = uuid.UUID(raw_data_id)
        with (
            track_task_execution(task_name),
            mlflow_task_run(
                task_name,
                raw_data_id=raw_uuid,
                correlation_id=correlation_id,
                params={"pipeline": "correlation_fusion"},
            ),
        ):
            with session_scope() as session:
                result = fuse_candidates_for_raw(session, raw_uuid)
            for key, value in result.items():
                mlflow.log_metric(f"relationships_{key}", value)
    except Exception:
        logger.exception(
            "task.failed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        raise
    else:
        logger.info(
            "task.completed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        return raw_data_id
    finally:
        pop_celery_context(task_token, correlation_token)


@celery_app.task(bind=True)
def export_obsidian_task(
    self,
    raw_data_id: str,
    export_path: str,
    *,
    correlation_id: str | None = None,
) -> str:
    """Export the specified dataset to an Obsidian-compatible vault."""
    task_name = self.name or "nexus_knowledge.tasks.export_obsidian_task"
    task_id, task_token, correlation_token = _bind_task_context(self, correlation_id)
    logger.info(
        "task.started",
        extra={
            "task_name": task_name,
            "task_id": task_id,
            "raw_data_id": raw_data_id,
            "export_path": export_path,
        },
    )
    try:
        raw_uuid = uuid.UUID(raw_data_id)
        with (
            track_task_execution(task_name),
            mlflow_task_run(
                task_name,
                raw_data_id=raw_uuid,
                correlation_id=correlation_id,
                params={"export_path": export_path},
            ),
        ):
            with session_scope() as session:
                exported_files = export_to_obsidian(session, raw_uuid, export_path)
            for exported in exported_files:
                log_task_artifact(exported)
            mlflow.log_metric("files_exported", len(exported_files))
    except Exception:
        logger.exception(
            "task.failed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        raise
    else:
        logger.info(
            "task.completed",
            extra={"task_name": task_name, "task_id": task_id},
        )
        return raw_data_id
    finally:
        pop_celery_context(task_token, correlation_token)


__all__ = [
    "analyze_raw_data_task",
    "celery_app",
    "export_obsidian_task",
    "fuse_correlation_candidates_task",
    "generate_correlation_candidates_task",
    "normalize_raw_data_task",
    "persist_feedback",
]
