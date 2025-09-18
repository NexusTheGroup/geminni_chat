from __future__ import annotations

import mlflow
import pytest

from nexus_knowledge.analysis import run_analysis_for_raw_data
from nexus_knowledge.analysis.pipeline import AnalysisError
from nexus_knowledge.db import repository
from nexus_knowledge.ingestion import ingest_raw_payload, normalize_raw_data


def _sample_payload() -> dict:
    return {
        "source_platform": "deepseek",
        "source_id": "analysis-1",
        "messages": [
            {
                "role": "user",
                "content": "I love this feature",
                "timestamp": "2025-01-01T00:00:00Z",
            },
            {
                "role": "assistant",
                "content": "I'm sorry to hear that",
                "timestamp": "2025-01-01T00:00:05Z",
            },
        ],
    }


def test_run_analysis_logs_entities(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    tracking_uri = (tmp_path / "mlruns").as_uri()
    monkeypatch.setenv("MLFLOW_TRACKING_URI", tracking_uri)

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_sample_payload(),
            source_id="analysis-1",
        )

    with session_factory.begin() as session:
        normalize_raw_data(session, raw_id)

    with session_factory.begin() as session:
        entity_count = run_analysis_for_raw_data(session, raw_id)

    assert entity_count == 2

    with session_factory() as session:
        record = repository.get_raw_data(session, raw_id)
        assert record is not None
        assert record.status == "ANALYZED"

    mlflow.set_tracking_uri(tracking_uri)
    runs = mlflow.search_runs(experiment_names=["Analysis"])
    assert not runs.empty


def test_run_analysis_without_turns_marks_failure(
    sqlite_db,
    tmp_path,
    monkeypatch,
) -> None:
    _, session_factory, _ = sqlite_db
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content={"messages": []},
        )

    with session_factory.begin() as session, pytest.raises(AnalysisError):
        run_analysis_for_raw_data(session, raw_id)

    with session_factory() as session:
        record = repository.get_raw_data(session, raw_id)
        assert record is not None
        assert record.status in {"FAILED", "ANALYSIS_FAILED"}
