from __future__ import annotations

import mlflow
from nexus_knowledge import mlflow_utils


def test_log_dummy_experiment(tmp_path, monkeypatch) -> None:
    tracking_uri = tmp_path.as_uri()
    monkeypatch.setenv("MLFLOW_TRACKING_URI", tracking_uri)

    run_id = mlflow_utils.log_dummy_experiment(run_name="test-run")

    mlflow_utils.configure_mlflow(tracking_uri)
    run = mlflow.get_run(run_id)
    assert run.data.params["component"] == "mlflow_integration"


def test_ensure_local_store_exists(tmp_path) -> None:
    target = tmp_path / "mlruns"
    mlflow_utils.ensure_local_store_exists(target)
    assert target.exists()
