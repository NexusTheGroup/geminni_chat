from __future__ import annotations

import pytest
from nexus_knowledge.ingestion import ingest_raw_payload, normalize_raw_data
from nexus_knowledge.search import hybrid_search
from nexus_knowledge.search.service import SearchError


def _payload() -> dict:
    return {
        "source_platform": "deepseek",
        "source_id": "search-1",
        "messages": [
            {
                "role": "user",
                "content": "I love hybrid search",
                "timestamp": "2025-01-01T00:00:00Z",
            },
            {
                "role": "assistant",
                "content": "Hybrid search combines keyword and semantic recall",
                "timestamp": "2025-01-01T00:00:05Z",
            },
        ],
    }


def test_hybrid_search_returns_results(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_payload(),
        )
        normalize_raw_data(session, raw_id)

    with session_factory() as session:
        results = hybrid_search(session, "hybrid search", limit=5)

    assert results
    assert results[0]["score"] > 0
    assert "hybrid" in results[0]["snippet"].lower()


def test_hybrid_search_requires_tokens(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db

    with session_factory() as session, pytest.raises(SearchError):
        hybrid_search(session, "   ")
