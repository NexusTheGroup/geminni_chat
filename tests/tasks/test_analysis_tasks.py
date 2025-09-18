from __future__ import annotations

from nexus_knowledge.db import repository
from nexus_knowledge.ingestion import ingest_raw_payload
from nexus_knowledge.ingestion.service import normalize_raw_data
from nexus_knowledge.tasks import analyze_raw_data_task, normalize_raw_data_task


def _payload() -> dict:
    return {
        "source_platform": "deepseek",
        "source_id": "task-analysis",
        "messages": [
            {
                "role": "user",
                "content": "I love this",
                "timestamp": "2025-01-01T00:00:00Z",
            },
            {
                "role": "assistant",
                "content": "I'm sorry",
                "timestamp": "2025-01-01T00:00:05Z",
            },
        ],
    }


def test_normalize_raw_data_task(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_payload(),
        )

    result = normalize_raw_data_task.apply(args=(str(raw_id),)).get()
    assert result == str(raw_id)

    with session_factory() as session:
        turns = repository.list_turns_for_raw(session, raw_id)
        assert len(turns) == 2
        record = repository.get_raw_data(session, raw_id)
        assert record.status == "NORMALIZED"


def test_analyze_raw_data_task(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_payload(),
        )
        normalize_raw_data(session, raw_id)

    result = analyze_raw_data_task.apply(args=(str(raw_id),)).get()
    assert result == str(raw_id)

    with session_factory() as session:
        record = repository.get_raw_data(session, raw_id)
        assert record.status == "ANALYZED"
