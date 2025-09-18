from __future__ import annotations

from pathlib import Path

from nexus_knowledge.analysis import run_analysis_for_raw_data
from nexus_knowledge.correlation import generate_candidates_for_raw
from nexus_knowledge.ingestion import ingest_raw_payload, normalize_raw_data
from nexus_knowledge.tasks import export_obsidian_task


def _payload() -> dict:
    return {
        "source_platform": "deepseek",
        "source_id": "export-task",
        "messages": [
            {
                "role": "user",
                "content": "Export task",
                "timestamp": "2025-01-01T00:00:00Z",
            },
            {
                "role": "assistant",
                "content": "Generates markdown",
                "timestamp": "2025-01-01T00:00:05Z",
            },
        ],
    }


def test_export_obsidian_task(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_payload(),
        )
        normalize_raw_data(session, raw_id)
        run_analysis_for_raw_data(session, raw_id)
        generate_candidates_for_raw(session, raw_id)

    export_path = tmp_path / "obsidian"

    result = export_obsidian_task.apply(args=(str(raw_id), str(export_path))).get()
    assert result == str(raw_id)

    generated = list(Path(export_path).glob("*.md"))
    assert generated
