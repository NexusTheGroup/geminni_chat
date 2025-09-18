from __future__ import annotations

from nexus_knowledge.db import repository
from nexus_knowledge.ingestion import (
    IngestionError,
    ingest_markdown_file,
    ingest_raw_payload,
    normalize_raw_data,
)


def _conversation_payload() -> dict:
    return {
        "source_platform": "deepseek",
        "source_id": "deepseek-chat-1",
        "messages": [
            {"role": "user", "content": "Hello", "timestamp": "2025-01-01T00:00:00Z"},
            {
                "role": "assistant",
                "content": "Hi!",
                "timestamp": "2025-01-01T00:00:05Z",
            },
        ],
    }


def test_ingest_and_normalize_single_conversation(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            source_id="deepseek-chat-1",
            content=_conversation_payload(),
            metadata={"dataset": "unit-test"},
        )

    with session_factory.begin() as session:
        processed_count = normalize_raw_data(session, raw_id)

    assert processed_count == 2

    with session_factory() as session:
        record = repository.get_raw_data(session, raw_id)
        assert record is not None
        assert record.status == "NORMALIZED"


def test_ingest_raw_payload_is_idempotent(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db
    payload = _conversation_payload()

    with session_factory.begin() as session:
        first_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=payload,
        )

    with session_factory.begin() as session:
        second_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=payload,
            metadata={"extra": True},
        )

    assert first_id == second_id

    with session_factory() as session:
        record = repository.get_raw_data(session, first_id)
        assert record is not None
        assert record.content_hash is not None
        assert record.metadata_["extra"] is True


def test_ingest_nested_conversations_structure(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db
    nested_payload = {
        "username": "user",
        "conversations": [
            _conversation_payload(),
            {
                "title": "second",
                "source_platform": "deepseek",
                "source_id": "deepseek-chat-2",
                "messages": [
                    {
                        "role": "user",
                        "content": "Ping",
                        "timestamp": "2025-02-01T00:00:00Z",
                    },
                ],
            },
        ],
    }

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            source_id="dataset-root",
            content=nested_payload,
        )

    with session_factory.begin() as session:
        processed_count = normalize_raw_data(session, raw_id)

    assert processed_count == 3


def test_ingest_markdown_file_normalizes_single_turn(sqlite_db, tmp_path) -> None:
    _, session_factory, _ = sqlite_db
    markdown_path = tmp_path / "note.md"
    markdown_path.write_text("# Title\n\nBody text", encoding="utf-8")

    with session_factory.begin() as session:
        raw_id = ingest_markdown_file(
            session,
            markdown_path,
            dataset="unit-tests",
            tags=["import", "markdown"],
        )

    with session_factory.begin() as session:
        processed_count = normalize_raw_data(session, raw_id)

    assert processed_count == 1

    with session_factory() as session:
        record = repository.get_raw_data(session, raw_id)
        assert record is not None
        assert record.metadata_["title"] == "Title"
        assert set(record.metadata_["tags"]) == {"import", "markdown"}

    with session_factory.begin() as session:
        duplicate_id = ingest_markdown_file(session, markdown_path)

    assert duplicate_id == raw_id


def test_normalize_handles_invalid_json(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db
    invalid_payload = "{"  # malformed

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            source_id="broken",
            content=invalid_payload,
        )

    with session_factory.begin() as session:
        try:
            normalize_raw_data(session, raw_id)
        except IngestionError:
            pass

    with session_factory() as session:
        record = repository.get_raw_data(session, raw_id)
        assert record is not None
        assert record.status == "FAILED"
