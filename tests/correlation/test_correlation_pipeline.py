from __future__ import annotations

import pytest
from nexus_knowledge.analysis import run_analysis_for_raw_data
from nexus_knowledge.correlation import generate_candidates_for_raw
from nexus_knowledge.correlation.pipeline import (
    CorrelationError,
    fuse_candidates_for_raw,
)
from nexus_knowledge.db import repository
from nexus_knowledge.ingestion import ingest_raw_payload, normalize_raw_data


def _payload() -> dict:
    return {
        "source_platform": "deepseek",
        "source_id": "correlation-1",
        "messages": [
            {
                "role": "user",
                "content": "I love this product",
                "timestamp": "2025-01-01T00:00:00Z",
            },
            {
                "role": "assistant",
                "content": "That is great!",
                "timestamp": "2025-01-01T00:00:02Z",
            },
            {
                "role": "user",
                "content": "I love this feature",
                "timestamp": "2025-01-01T00:00:04Z",
            },
        ],
    }


def test_generate_candidates_for_raw(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_payload(),
        )

    with session_factory.begin() as session:
        normalize_raw_data(session, raw_id)

    with session_factory.begin() as session:
        run_analysis_for_raw_data(session, raw_id)

    with session_factory.begin() as session:
        candidate_count = generate_candidates_for_raw(session, raw_id)

    assert candidate_count >= 1

    with session_factory() as session:
        candidates = repository.list_correlation_candidates(session, raw_id)
        assert candidates
        assert all(candidate.status == "PENDING" for candidate in candidates)
        record = repository.get_raw_data(session, raw_id)
        assert record.status == "CORRELATION_GENERATED"


def test_generate_candidates_without_entities(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content={"messages": [{"role": "user", "content": "Hello"}]},
        )

    with session_factory.begin() as session:
        normalize_raw_data(session, raw_id)

    with session_factory.begin() as session:
        with pytest.raises(CorrelationError):
            generate_candidates_for_raw(session, raw_id)


def test_fuse_candidates_for_raw(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_payload(),
        )

    with session_factory.begin() as session:
        normalize_raw_data(session, raw_id)
        run_analysis_for_raw_data(session, raw_id)
        generate_candidates_for_raw(session, raw_id)

    with session_factory.begin() as session:
        result = fuse_candidates_for_raw(session, raw_id)

    assert result["confirmed"] >= 1

    with session_factory() as session:
        relationships = repository.list_relationships_for_raw(session, raw_id)
        assert relationships
        record = repository.get_raw_data(session, raw_id)
        assert record.status == "CORRELATED"
