from __future__ import annotations

from sqlalchemy import inspect

EXPECTED_TABLES = {
    "raw_data",
    "conversation_turns",
    "entities",
    "relationships",
    "user_feedback",
    "mlflow_runs",
    "dvc_data_assets",
}


def test_expected_tables_exist(sqlite_db) -> None:
    _, _, engine = sqlite_db
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert EXPECTED_TABLES.issubset(tables)
