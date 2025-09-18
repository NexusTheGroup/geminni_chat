"""Experiment tracking helpers for Celery tasks."""

from __future__ import annotations

import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import mlflow
from nexus_knowledge.mlflow_utils import configure_mlflow
from nexus_knowledge.observability import get_celery_task_id, get_correlation_id


@contextmanager
def mlflow_task_run(
    task_name: str,
    *,
    raw_data_id: uuid.UUID | None = None,
    correlation_id: str | None = None,
    tracking_uri: str | None = None,
    tags: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> Iterator[str]:
    """Start an MLflow run for a Celery task and log basic metadata.

    Yields the run identifier so callers can associate artifacts or metrics.
    """
    configure_mlflow(tracking_uri)
    active_run = mlflow.active_run()
    if active_run is None:
        mlflow.set_experiment("CeleryTasks")
    start_kwargs: dict[str, Any] = {"run_name": f"task::{task_name}"}
    if active_run is not None:
        start_kwargs["nested"] = True
    start = time.perf_counter()

    base_tags: dict[str, Any] = {
        "component": "celery_task",
        "task_name": task_name,
    }

    corr = correlation_id or get_correlation_id()
    if corr:
        base_tags["correlation_id"] = corr

    celery_task_id = get_celery_task_id()
    if celery_task_id:
        base_tags["celery_task_id"] = celery_task_id

    if raw_data_id is not None:
        base_tags["raw_data_id"] = str(raw_data_id)

    all_tags = {**base_tags, **(tags or {})}
    all_params = dict(params or {})
    if raw_data_id is not None:
        all_params.setdefault("raw_data_id", str(raw_data_id))

    with mlflow.start_run(**start_kwargs) as active_run:
        if all_tags:
            mlflow.set_tags(all_tags)
        if all_params:
            mlflow.log_params(all_params)
        try:
            yield active_run.info.run_id
        except Exception:
            mlflow.set_tag("status", "failed")
            raise
        else:
            mlflow.set_tag("status", "succeeded")
        finally:
            duration = time.perf_counter() - start
            mlflow.log_metric("duration_seconds", duration)


def log_task_artifact(path: str | Path) -> None:
    """Attach a file or directory as a task artifact in the active MLflow run."""
    path_obj = Path(path)
    if path_obj.is_dir():
        mlflow.log_artifacts(str(path_obj))
    elif path_obj.is_file():
        mlflow.log_artifact(str(path_obj))


__all__ = ["mlflow_task_run", "log_task_artifact"]
