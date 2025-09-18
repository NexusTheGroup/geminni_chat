"""Obsidian export helpers with deterministic filenames and metadata."""

from __future__ import annotations

import re
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nexus_knowledge.db.repository import get_raw_data, list_turns_for_raw
from sqlalchemy.orm import Session


class ExportError(RuntimeError):
    """Raised when an export operation fails."""


def export_to_obsidian(
    session: Session,
    raw_data_id: uuid.UUID,
    export_path: str,
) -> list[Path]:
    """Export a conversation to Obsidian-flavoured Markdown.

    Returns a list of created files (currently a single note).
    """
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise ExportError(f"raw_data {raw_data_id} not found")

    turns: Sequence = list_turns_for_raw(session, raw_data_id)
    if not turns:
        raise ExportError("No turns available to export")

    export_dir = Path(export_path)
    export_dir.mkdir(parents=True, exist_ok=True)

    metadata: dict[str, Any] = dict(record.metadata_ or {})
    if isinstance(metadata.get("tags"), list):
        metadata["tags"] = sorted(
            str(tag) for tag in metadata["tags"] if tag is not None
        )
    title = str(metadata.get("title") or f"Conversation {raw_data_id}")
    slug = _slugify(title) or raw_data_id.hex
    file_path = export_dir / f"{slug}.md"

    frontmatter = _build_frontmatter(
        {
            "version": "1.0",
            "raw_data_id": str(raw_data_id),
            "source_type": record.source_type,
            "source_id": record.source_id,
            "content_hash": record.content_hash,
            "title": title,
            "exported_at": datetime.now(UTC).isoformat(),
            **metadata,
        },
    )

    body_lines: list[str] = [f"# {title}"]
    for turn in turns:
        heading = f"## {turn.speaker.title()} - turn {turn.turn_index}"
        body_lines.append(heading)
        timestamp = turn.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        body_lines.append(timestamp.isoformat())
        text = (turn.text or "").strip()
        if text:
            body_lines.append("")
            body_lines.append(text)
        body_lines.append("")

    content = (
        frontmatter + "\n".join(line.rstrip() for line in body_lines).rstrip() + "\n"
    )
    file_path.write_text(content, encoding="utf-8")
    return [file_path]


def _build_frontmatter(payload: dict[str, Any]) -> str:
    lines: list[str] = ["---"]
    for key in sorted(payload):
        value = payload[key]
        if value is None:
            continue
        lines.extend(_format_yaml_entry(key, value))
    lines.append("---\n")
    return "\n".join(lines)


def _format_yaml_entry(key: str, value: Any) -> list[str]:
    if isinstance(value, list):
        items = [f"{key}:"]
        for item in value:
            items.append(f"  - {_escape_yaml_value(item)}")
        return items
    if isinstance(value, dict):
        items = [f"{key}:"]
        for child_key in sorted(value):
            child_value = value[child_key]
            if child_value is None:
                continue
            child_lines = _format_yaml_entry(child_key, child_value)
            items.extend([f"  {line}" for line in child_lines])
        return items
    return [f"{key}: {_escape_yaml_value(value)}"]


def _escape_yaml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if not text:
        return "''"
    if any(char in text for char in ":#[]{}\n\r") or text.strip() != text:
        escaped = text.replace('"', '\\"')
        return f'"{escaped}"'
    return text


def _slugify(value: str) -> str | None:
    normalised = value.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", normalised)
    slug = cleaned.strip("-")
    return slug or None
