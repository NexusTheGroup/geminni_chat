# P11: Import/Export & Interoperability Specification

This document defines the technical specifications for Phase 11, addressing the goals of robust data import, deterministic Obsidian export, and stable interoperability formats.

## 1. Goals & Scope

- **Import**: Finalize ingestion connectors for permitted sources (starting with Markdown files), ensuring idempotency and metadata capture.
- **Export**: Implement a robust Obsidian export flow with deterministic file paths, clean content, and metadata retention.
- **Interop**: Define versioned file formats/schemas for import/export and a policy for breaking changes.

## 2. Canonical Data Model

The target for all normalization is the existing SQLAlchemy data model defined in `src/nexus_knowledge/db/models.py`. The primary tables for this phase are:

- `raw_data`: Stores the original ingested content and metadata.
- `conversation_turns`: Stores the normalized, atomic pieces of a conversation.

## 3. Import Process

### 3.1. Permitted Source: Markdown Files

- **Source Type Identifier**: `markdown`
- **Content**: The raw text content of the `.md` file.
- **Normalization**: A Markdown file will be treated as a single-turn conversation.
  - A `RawData` record is created with `source_type='markdown'`.
  - A single `ConversationTurn` record is created.
    - `speaker`: 'USER'
    - `text`: The full content of the Markdown file.
    - `timestamp`: The file's modification time or the time of ingestion.

### 3.2. Idempotency Strategy

To prevent duplicate imports of the same content, the following strategy will be implemented:

1.  **Database Migration**: A new column `content_hash` (SHA-256) will be added to the `raw_data` table. This column will have a unique constraint.
2.  **Ingestion Workflow**:
    - Before creating a `RawData` record, the ingestion service will compute the SHA-256 hash of the incoming content.
    - It will query the database for an existing record with the same `content_hash`.
    - If a match is found, the ingestion is skipped, and the ID of the existing record is returned.
    - If no match is found, a new record is created.

### 3.3. Import Data Format (Generic JSON)

For API-based ingestion, a generic versioned JSON format is defined.

**Version: 1.0**

```json
{
  "version": "1.0",
  "source_type": "markdown", // Or other permitted types
  "source_id": "optional-unique-id-from-source-system",
  "content": "The full text content of the document.",
  "metadata": {
    "title": "My Document Title",
    "tags": ["tag1", "tag2"],
    "created_at": "2025-09-18T12:00:00Z"
  }
}
```

## 4. Export Process (Obsidian)

The existing Obsidian export functionality will be enhanced.

### 4.1. File Naming

- File names will be generated from a `title` field in the `RawData` metadata.
- The title will be "slugified" (e.g., "My Document Title" -> `my-document-title.md`).
- If no title is available, the system will fall back to using the `raw_data_id` as the filename.

### 4.2. File Structure & Content

- **Frontmatter**: The Markdown files will contain a YAML frontmatter block with rich metadata.
- **Content**: The body will be the clean Markdown from the `ConversationTurn`.
- **Linking**: Standard Obsidian `[[wikilink]]` syntax will be supported. The export process will not initially validate links, but the format is designed for future expansion.

**Example Exported File (`my-document-title.md`):**

```markdown
---
version: 1.0
raw_data_id: "abc-123-def-456"
source_type: "markdown"
source_id: "optional-unique-id"
tags:
  - tag1
  - tag2
created_at: "2025-09-18T12:00:00Z"
exported_at: "2025-09-18T14:00:00Z"
---

# My Document Title

The full text content of the document.

This might include a [[link-to-another-note]].
```

### 4.3. Breaking Changes Policy

- The frontmatter will include a `version` field (e.g., `1.0`).
- Any change to the export format that is not backward-compatible will require incrementing the version number.
- Documentation in the `IMPORT_EXPORT_RUNBOOK.md` will detail the changes between versions.

## 5. Test Plan

1.  **Unit Tests**:
    - Test the new Markdown ingestion service.
    - Test the content hashing and idempotency check.
    - Test the slugification of titles for filenames.
    - Test the frontmatter generation logic.
2.  **Integration Tests**:
    - Test the full import-normalize flow for a Markdown file.
    - Run an import twice with the same content and assert that only one record is created.
3.  **Golden File Tests**:
    - Create a sample `RawData` record in the test database.
    - Run the Obsidian export against this record.
    - Compare the resulting `.md` file against a pre-written "golden" file. The test fails if they do not match exactly.

## 6. Implementation Outline

1.  **Database**: Create an Alembic migration to add the `content_hash` column to `raw_data`.
2.  **Ingestion**:
    - Modify `ingestion/service.py` to add `ingest_markdown_payload` and the hashing logic.
    - Update `tasks.py` with a new or modified normalization task for Markdown.
3.  **Export**:
    - Modify `export/obsidian.py` to implement the new file naming and frontmatter logic.
4.  **API**:
    - Update `api/main.py` to expose the new ingestion capabilities if necessary.
5.  **Tests**:
    - Add tests in `tests/ingestion/` and `tests/export/`.
6.  **Documentation**:
    - Create `docs/IMPORT_EXPORT_RUNBOOK.md`.
    - Update `docs/TODO.md`.
