"""Utility helpers for working with MLflow locally."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import mlflow

DEFAULT_MLFLOW_URI = "http://localhost:5000"


def get_tracking_uri() -> str:
    """Return the configured MLflow tracking URI."""
    return os.getenv("MLFLOW_TRACKING_URI", DEFAULT_MLFLOW_URI)


def configure_mlflow(tracking_uri: str | None = None) -> None:
    """Configure MLflow's global tracking URI."""
    mlflow.set_tracking_uri(tracking_uri or get_tracking_uri())


def log_dummy_experiment(
    run_name: str = "nexusknowledge-smoke",
    *,
    parameters: dict[str, Any] | None = None,
    tracking_uri: str | None = None,
) -> str:
    """Log a simple MLflow experiment to validate integration."""
    target_uri = tracking_uri or get_tracking_uri()
    configure_mlflow(target_uri)

    parsed = urlparse(target_uri)
    if parsed.scheme == "file" and parsed.path:
        ensure_local_store_exists(Path(parsed.path))
        mlflow.set_experiment("Default")

    params = parameters or {"phase": "P1", "component": "mlflow_integration"}
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", 0.0)
        mlflow.log_text("Dummy artifact for integration testing", "artifacts/info.txt")
        return run.info.run_id


def ensure_local_store_exists(path: str | Path) -> None:
    """Ensure the provided path exists for file-based MLflow backends."""
    store_path = Path(path)
    store_path.mkdir(parents=True, exist_ok=True)
