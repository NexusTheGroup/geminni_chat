from __future__ import annotations

import re
from pathlib import Path

from nexus_knowledge.analysis import run_analysis_for_raw_data
from nexus_knowledge.correlation import generate_candidates_for_raw
from nexus_knowledge.export.obsidian import ExportError, export_to_obsidian
from nexus_knowledge.ingestion import ingest_raw_payload, normalize_raw_data


def _payload() -> dict:
    return {
        "source_platform": "deepseek",
        "source_id": "export-1",
        "messages": [
            {
                "role": "user",
                "content": "I love this export feature",
                "timestamp": "2025-01-01T00:00:00Z",
            },
            {
                "role": "assistant",
                "content": "Exports can feed Obsidian",
                "timestamp": "2025-01-01T00:00:05Z",
            },
        ],
    }


def test_export_to_obsidian(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content=_payload(),
            metadata={"title": "Export Test", "tags": ["obsidian", "export"]},
        )
        normalize_raw_data(session, raw_id)
        run_analysis_for_raw_data(session, raw_id)
        generate_candidates_for_raw(session, raw_id)

    export_dir = tmp_path / "obsidian"

    with session_factory() as session:
        files = export_to_obsidian(session, raw_id, export_dir)

    assert len(files) == 1
    file_path = Path(files[0])
    assert file_path.name == "export-test.md"
    content = file_path.read_text(encoding="utf-8")

    expected = _load_golden("obsidian_basic.md")
    assert _normalise_dynamic_fields(content) == expected


def test_export_to_obsidian_requires_turns(sqlite_db, tmp_path) -> None:
    _, session_factory, _ = sqlite_db

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content={"messages": []},
        )

    with session_factory() as session:
        try:
            export_to_obsidian(session, raw_id, tmp_path)
        except ExportError:
            pass
        else:
            raise AssertionError("Expected ExportError for missing turns")


def _normalise_dynamic_fields(content: str) -> str:
    """Replace dynamic timestamps in export output for deterministic comparisons."""
    intermediate = re.sub(r"exported_at: .+", "exported_at: <timestamp>", content)
    return re.sub(r"raw_data_id: .+", "raw_data_id: <raw_data_id>", intermediate)


def _load_golden(name: str) -> str:
    golden_path = Path(__file__).parent / "golden" / name
    return golden_path.read_text(encoding="utf-8")
