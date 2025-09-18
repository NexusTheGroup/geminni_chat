from __future__ import annotations

import uuid

import mlflow
from mlflow.tracking import MlflowClient
from nexus_knowledge.experiment_tracking import log_task_artifact, mlflow_task_run


def test_mlflow_task_run_logs_metadata(tmp_path, monkeypatch) -> None:
    tracking_uri = tmp_path.as_uri()
    monkeypatch.setenv("MLFLOW_TRACKING_URI", tracking_uri)

    sample_file = tmp_path / "artifact.txt"
    sample_file.write_text("example", encoding="utf-8")

    raw_id = uuid.uuid4()
    with mlflow_task_run(
        "sample_task",
        raw_data_id=raw_id,
        correlation_id="corr-123",
        params={"foo": "bar"},
    ) as run_id:
        mlflow.log_metric("custom_metric", 1.0)
        log_task_artifact(sample_file)

    mlflow.set_tracking_uri(tracking_uri)
    run = mlflow.get_run(run_id)
    assert run.data.metrics["custom_metric"] == 1.0
    assert "duration_seconds" in run.data.metrics
    assert run.data.params["foo"] == "bar"
    assert run.data.params["raw_data_id"] == str(raw_id)
    assert run.data.tags["task_name"] == "sample_task"
    assert run.data.tags["correlation_id"] == "corr-123"
    assert run.data.tags["component"] == "celery_task"

    artifacts = MlflowClient().list_artifacts(run_id)
    assert any(item.path == "artifact.txt" for item in artifacts)
