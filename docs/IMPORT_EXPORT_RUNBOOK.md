# Import & Export Runbook (Phase P11)

This runbook captures the finalized ingestion connectors, idempotency mechanics, and Obsidian export workflow delivered in Phase P11. It complements `docs/P11_IMPORT_EXPORT_SPEC.md` with the executable details required by the personas.

## Supported Connectors

| Connector | Source Type               | Description                                                                                                                               | Entry Point                                      |
| --------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Markdown  | `markdown`                | Single-file Markdown knowledge notes. Each file becomes a single-turn conversation with metadata extracted from the filename/frontmatter. | `nexus_knowledge.ingestion.ingest_markdown_file` |
| JSON API  | `deepseek_chat` (example) | Generic JSON payloads posted through the ingestion API. Messages are flattened into the canonical conversation/turn model.                | `nexus_knowledge.ingestion.ingest_raw_payload`   |

> Additional connectors should follow the same pattern: serialise to canonical JSON (`messages`, optional `conversations`), call `ingest_raw_payload`, and reuse the idempotency helper described below.

## Idempotency & Metadata Capture

1. **Content Hash:** `ingest_raw_payload` canonicalises every payload (`json.dumps(..., sort_keys=True)`) and calculates a SHA-256 hash. The hash is persisted in `raw_data.content_hash` (unique index via Alembic revision `20250918_04`).
2. **Deduplication:** Before inserting new records we check `get_raw_data_by_hash`. Existing records are returned and metadata is merged, guaranteeing idempotent behaviour across Celery retries and manual replays.
3. **Metadata:**
   - `source_id` and user supplied metadata are retained on the existing record when duplicates occur.
   - Markdown connector enriches metadata with `title`, `source_path`, `source_modified_at`, `dataset`, and `tags` (sorted for determinism).

### Verification Steps

```bash
# Run ingestion unit tests covering idempotency + markdown connector
pytest tests/ingestion/test_service.py
```

## Obsidian Export Flow

- Export entry point: `nexus_knowledge.export.export_to_obsidian(session, raw_data_id, export_path)`.
- File naming: slugified `metadata.title` (fallback to UUID). Deterministic across runs.
- Frontmatter: YAML with versioned schema (`version: 1.0`), `raw_data_id`, `content_hash`, `source_type`, sorted metadata, and export timestamp.
- Body: Markdown heading per turn (`## Speaker - turn N`) with ISO timestamps and sanitised text.
- Artifacts: Celery export task logs the generated files to MLflow for provenance.

### Golden File Regression

`tests/export/test_obsidian.py` compares the generated Markdown (with timestamp/UUID normalised) against `tests/export/golden/obsidian_basic.md`. Update the golden file only when intentionally changing the export schema.

### Manual Smoke Test

```bash
# 1) Ingest and normalise a markdown note
python - <<'PY'
from pathlib import Path
from nexus_knowledge.db.session import session_scope
from nexus_knowledge.ingestion import ingest_markdown_file, normalize_raw_data
from nexus_knowledge.export import export_to_obsidian
import uuid

note = Path("/tmp/note.md")
note.write_text("# Notebook\n\nContent", encoding="utf-8")

with session_scope() as session:
    raw_id = ingest_markdown_file(session, note, dataset="manual")
    normalize_raw_data(session, raw_id)
    files = export_to_obsidian(session, raw_id, "/tmp/obsidian")
    print("Exported:", files)
PY
```

## Change Log & Cross Links

- Runbook maintained here, linked from `docs/BUILD_PLAN.md` (Phase P11) and `docs/TODO.md` validation notes.
- Schema migration: `alembic/versions/20250918_04_add_content_hash_to_raw_data.py`.
- Tests: `tests/ingestion/test_service.py`, `tests/export/test_obsidian.py`.

Always enforce Celery execution for long-running imports/exports; orchestrator tasks should queue work via the existing Celery tasks (`normalize_raw_data_task`, `export_obsidian_task`).
