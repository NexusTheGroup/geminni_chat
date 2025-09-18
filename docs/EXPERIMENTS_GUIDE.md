# Experiment Tracking & Reproducibility Guide (Phase P12)

This guide documents the MLflow and DVC patterns introduced in Phase P12. It is the canonical reference for personas operating the experiment stack.

## Testing Configuration

### File-Based MLflow Backend

In tests, MLflow is configured to use a file-based backend by default:

- `MLFLOW_TRACKING_URI` defaults to `file://./mlruns` in test environments
- No MLflow server required for testing
- Experiment tracking data is stored locally in the `mlruns` directory
- Tests automatically clean up tracking data between runs

### Nested Run Behavior

The `mlflow_task_run` wrapper supports nested runs, which is important for testing:

- Tasks can be executed within existing MLflow runs without conflict
- Nested runs maintain proper parent-child relationships
- Context is properly propagated and cleaned up
- Safe to use in unit tests that may create multiple runs

## MLflow Task Wrappers

### Overview

- All Celery tasks that transform `raw_data` now use `nexus_knowledge.experiment_tracking.mlflow_task_run`.
- The wrapper automatically:
  - Configures the tracking URI (`MLFLOW_TRACKING_URI`, defaults to `http://localhost:5000`).
  - Starts a nested MLflow run named `task::<task_name>`.
  - Sets tags: `component=celery_task`, `task_name`, `raw_data_id`, `correlation_id` (when present), `celery_task_id`.
  - Logs provided params and measures `duration_seconds`.
  - Marks status (`status=succeeded/failed`).

### Usage Pattern

```python
from nexus_knowledge.experiment_tracking import mlflow_task_run
import mlflow

with mlflow_task_run(
    "normalize_raw_data_task",
    raw_data_id=raw_uuid,
    correlation_id=correlation_id,
    params={"pipeline": "normalization"},
):
    processed = normalize_raw_data(session, raw_uuid)
    mlflow.log_metric("turns_normalized", processed)
```

Artifacts can be attached using `nexus_knowledge.experiment_tracking.log_task_artifact(path)` within the context.

### Validation

```
pytest tests/mlflow/test_experiment_tracking.py
```

## DVC Data Versioning

### Pipeline

- `dvc.yaml` defines the `prepare_sample` stage:
  - Command: `python scripts/dvc/prepare_sample_dataset.py --input sample_data.json --output data/processed/sample_data.json`
  - Dependencies: source JSON + script.
  - Output: processed dataset stored under `data/processed/` (git-ignored, tracked by DVC).

### Workflow

1. **Reproduce stage**
   ```bash
   dvc repro prepare_sample
   ```
2. **Inspect status**
   ```bash
   dvc status
   ```
3. **Push to remote** (configure once via `dvc remote add origin <path-or-s3-uri>`)
   ```bash
   dvc push origin
   ```

`tests/dvc/test_pipeline.py` runs `dvc repro` to confirm the stage builds and cleans up the generated artifact afterwards.

### Governance

- Keep large datasets out of Git; use DVC outs for deterministic regeneration.
- Group artifacts under `data/processed/<dataset>/<version>` when adding new stages.
- Document new pipelines in this guide; update `docs/TODO.md` validation checklist accordingly.

## Reproducibility Checklist

1. Set `MLFLOW_TRACKING_URI` and ensure the MLflow server is running (`docker compose up mlflow`).
2. Activate the virtualenv: `source venv/bin/activate`.
3. Run data pipeline: `dvc repro prepare_sample`.
4. Launch Celery worker + API (`docker compose up worker api`).
5. Trigger ingestion, analysis, correlation via API or runbook scripts.
6. Open MLflow UI to inspect task runs, metrics (`duration_seconds`, `turns_*`, `files_exported`).
7. Optionally call `log_task_artifact` within tasks to capture exported Markdown for audit.

Cross-links:

- See `docs/IMPORT_EXPORT_RUNBOOK.md` for the complementary P11 workflow.
- `docs/TODO.md` (P12 section) lists validation commands.
- CHANGELOG updated with MLflow/DVC enhancements.
