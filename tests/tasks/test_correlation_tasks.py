from __future__ import annotations

from nexus_knowledge.db import repository
from nexus_knowledge.ingestion import ingest_raw_payload
from nexus_knowledge.tasks import (
    analyze_raw_data_task,
    fuse_correlation_candidates_task,
    generate_correlation_candidates_task,
    normalize_raw_data_task,
)


def _payload() -> dict:
    return {
        "source_platform": "deepseek",
        "source_id": "correlation-task",
        "messages": [
            {
                "role": "user",
                "content": "I love this",
                "timestamp": "2025-01-01T00:00:00Z",
            },
            {
                "role": "assistant",
                "content": "That is awesome",
                "timestamp": "2025-01-01T00:00:05Z",
            },
        ],
    }


def test_generate_correlation_candidates_task(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_payload(),
        )

    normalize_raw_data_task.apply(args=(str(raw_id),)).get()
    analyze_raw_data_task.apply(args=(str(raw_id),)).get()

    result = generate_correlation_candidates_task.apply(args=(str(raw_id),)).get()
    assert result == str(raw_id)

    with session_factory() as session:
        candidates = repository.list_correlation_candidates(session, raw_id)
        assert candidates
        record = repository.get_raw_data(session, raw_id)
        assert record.status == "CORRELATION_GENERATED"


def test_fuse_correlation_candidates_task(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_payload(),
        )

    normalize_raw_data_task.apply(args=(str(raw_id),)).get()
    analyze_raw_data_task.apply(args=(str(raw_id),)).get()
    generate_correlation_candidates_task.apply(args=(str(raw_id),)).get()

    result = fuse_correlation_candidates_task.apply(args=(str(raw_id),)).get()
    assert result == str(raw_id)

    with session_factory() as session:
        relationships = repository.list_relationships_for_raw(session, raw_id)
        assert relationships
        record = repository.get_raw_data(session, raw_id)
        assert record.status == "CORRELATED"
