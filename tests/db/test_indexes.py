from __future__ import annotations

from sqlalchemy import text


def _index_names(engine, table: str) -> set[str]:
    with engine.connect() as connection:
        result = connection.execute(text(f"PRAGMA index_list('{table}')"))
        return {row[1] for row in result}


def test_performance_indexes_created(sqlite_db) -> None:
    _, _, engine = sqlite_db

    raw_indexes = _index_names(engine, "raw_data")
    assert "idx_raw_data_source_type_status" in raw_indexes

    turns_indexes = _index_names(engine, "conversation_turns")
    assert "idx_conversation_turns_raw_data_turn_index" in turns_indexes

    candidate_indexes = _index_names(engine, "correlation_candidates")
    assert "idx_correlation_candidates_raw_status" in candidate_indexes
