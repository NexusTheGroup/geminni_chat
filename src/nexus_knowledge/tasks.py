import logging
import os
import time
import uuid
from typing import Any

from celery import Celery
from nexus_knowledge.analysis.pipeline import run_analysis_for_raw_data
from nexus_knowledge.correlation import generate_candidates_for_raw
from nexus_knowledge.correlation.pipeline import fuse_candidates_for_raw
from nexus_knowledge.db.repository import create_user_feedback
from nexus_knowledge.db.session import session_scope
from nexus_knowledge.export import export_to_obsidian
from nexus_knowledge.ingestion.service import normalize_raw_data

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("nexus_knowledge_tasks", broker=REDIS_URL, backend=REDIS_URL)
logger = logging.getLogger(__name__)


@celery_app.task
def long_running_api_call(input_string: str) -> str:
    """Simulate a long-running API call to an AI model."""
    logger.info("Starting long_running_api_call with: %s", input_string)
    time.sleep(2)  # Simulate network latency without blocking the main thread.
    result = f"Processed '{input_string}' at {time.ctime()}"
    logger.info("Finished long_running_api_call: %s", result)
    return result


@celery_app.task
def persist_feedback(feedback_id: str, payload: dict[str, Any]) -> str:
    """Persist user feedback asynchronously to keep the API responsive."""
    with session_scope() as session:
        create_user_feedback(
            session,
            feedback_id=uuid.UUID(feedback_id),
            feedback_type=payload["feedback_type"],
            message=payload["message"],
            user_id=uuid.UUID(payload["user_id"]) if payload.get("user_id") else None,
        )
    return feedback_id


@celery_app.task
def normalize_raw_data_task(raw_data_id: str) -> str:
    """Normalize the stored raw payload into conversation turns."""
    with session_scope() as session:
        normalize_raw_data(session, uuid.UUID(raw_data_id))
    return raw_data_id


@celery_app.task
def analyze_raw_data_task(raw_data_id: str) -> str:
    """Run sentiment analysis on normalized conversation turns."""
    with session_scope() as session:
        run_analysis_for_raw_data(session, uuid.UUID(raw_data_id))
    return raw_data_id


@celery_app.task
def generate_correlation_candidates_task(raw_data_id: str) -> str:
    """Generate correlation candidates for a raw payload."""
    with session_scope() as session:
        generate_candidates_for_raw(session, uuid.UUID(raw_data_id))
    return raw_data_id


@celery_app.task
def fuse_correlation_candidates_task(raw_data_id: str) -> str:
    """Fuse correlation candidates into relationships."""
    with session_scope() as session:
        fuse_candidates_for_raw(session, uuid.UUID(raw_data_id))
    return raw_data_id


@celery_app.task
def export_obsidian_task(raw_data_id: str, export_path: str) -> str:
    """Export the specified dataset to an Obsidian-compatible vault."""
    with session_scope() as session:
        export_to_obsidian(session, uuid.UUID(raw_data_id), export_path)
    return raw_data_id
