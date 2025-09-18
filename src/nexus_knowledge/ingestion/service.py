"""Ingestion pipeline for storing and normalizing conversation data."""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TypeAlias

from nexus_knowledge.db.models import ConversationTurn
from nexus_knowledge.db.repository import (
    create_conversation_turns,
    create_raw_data,
    get_raw_data,
    get_raw_data_by_hash,
    update_raw_data_status,
)
from sqlalchemy.orm import Session

JSONPrimitive = str | int | float | bool | None
JSONValue: TypeAlias = JSONPrimitive | dict[str, "JSONValue"] | list["JSONValue"]
JSONDict: TypeAlias = dict[str, JSONValue]
MessagePayload: TypeAlias = dict[str, JSONValue]


class IngestionError(RuntimeError):
    """Raised when ingestion or normalization fails."""


@dataclass
class ConversationPayload:
    """Flattened representation of a conversation ready for normalization."""

    metadata: JSONDict
    messages: list[MessagePayload]


def ingest_raw_payload(
    session: Session,
    *,
    source_type: str,
    content: JSONValue,
    metadata: JSONDict | None = None,
    source_id: str | None = None,
) -> uuid.UUID:
    """Persist raw ingestion payload and return its identifier."""
    serialized = _serialise_content(content)
    content_hash = _compute_content_hash(serialized)
    metadata_payload = dict(metadata or {})
    if source_id:
        metadata_payload.setdefault("source_id", source_id)

    existing = get_raw_data_by_hash(session, content_hash)
    if existing is not None:
        merged_metadata = {**(existing.metadata_ or {}), **metadata_payload}
        if merged_metadata != existing.metadata_:
            existing.metadata_ = merged_metadata
        if source_id and not existing.source_id:
            existing.source_id = source_id
        session.flush()
        return existing.id

    record = create_raw_data(
        session,
        source_type=source_type,
        content=serialized,
        source_id=source_id,
        metadata=metadata_payload,
        content_hash=content_hash,
    )
    return record.id


def ingest_markdown_file(
    session: Session,
    path: str | Path,
    *,
    dataset: str | None = None,
    tags: Sequence[str] | None = None,
) -> uuid.UUID:
    """Ingest a Markdown document as a single-turn conversation."""
    file_path = Path(path)
    content = file_path.read_text(encoding="utf-8")
    title = _extract_markdown_title(content) or file_path.stem
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=UTC)

    metadata: JSONDict = {
        "title": title,
        "source_path": str(file_path.resolve()),
        "source_filename": file_path.name,
        "source_modified_at": mtime.isoformat(),
        "imported_at": datetime.now(UTC).isoformat(),
    }
    if dataset:
        metadata["dataset"] = dataset
    if tags:
        metadata["tags"] = list(tags)

    payload: JSONDict = {
        "version": "1.0",
        "source_platform": "markdown",
        "source_id": str(file_path.resolve()),
        "messages": [
            {
                "role": "user",
                "content": content,
                "timestamp": mtime.isoformat(),
            },
        ],
    }

    return ingest_raw_payload(
        session,
        source_type="markdown",
        content=payload,
        metadata=metadata,
        source_id=str(file_path.resolve()),
    )


def normalize_raw_data(session: Session, record_id: uuid.UUID) -> int:
    """Transform raw data entry into normalized conversation turns."""
    record = get_raw_data(session, record_id)
    if record is None:
        raise IngestionError(f"raw_data {record_id} not found")

    try:
        payload = json.loads(record.content)
    except json.JSONDecodeError as exc:
        update_raw_data_status(session, record_id, status="FAILED")
        raise IngestionError("Failed to decode raw content") from exc

    conversations = _flatten_conversations(payload)
    if not conversations:
        update_raw_data_status(session, record_id, status="FAILED")
        raise IngestionError("No conversations found in payload")

    turns: list[ConversationTurn] = []

    for conversation in conversations:
        conversation_id = _resolve_conversation_id(conversation.metadata)
        source_platform_value = conversation.metadata.get("source_platform")
        if source_platform_value is None:
            source_platform_value = conversation.metadata.get("sourcePlatform")
        source_platform = (
            str(source_platform_value)
            if isinstance(source_platform_value, str)
            else None
        )
        for index, message in enumerate(conversation.messages):
            speaker = str(message.get("role", "unknown")).upper()
            text = str(message.get("content", "")).strip()
            timestamp = _parse_timestamp(message.get("timestamp"))
            message_metadata = {
                "source_platform": source_platform,
                "role": message.get("role"),
                "metadata": message.get("metadata", {}),
            }
            turns.append(
                ConversationTurn(
                    raw_data_id=record.id,
                    conversation_id=conversation_id,
                    turn_index=index,
                    speaker=speaker,
                    text=text,
                    timestamp=timestamp,
                    metadata_=message_metadata,
                ),
            )

    create_conversation_turns(session, turns)
    update_raw_data_status(
        session,
        record_id,
        status="NORMALIZED",
        processed_at=datetime.now(UTC),
    )
    return len(turns)


def _serialise_content(content: JSONValue) -> str:
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False, sort_keys=True)


def _compute_content_hash(serialized_content: str) -> str:
    return hashlib.sha256(serialized_content.encode("utf-8")).hexdigest()


def _extract_markdown_title(content: str) -> str | None:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("# ").strip() or None
    return None


def _flatten_conversations(  # noqa: C901
    payload: JSONValue,
) -> Sequence[ConversationPayload]:
    """Extract conversations + messages from heterogeneous payloads."""
    conversations: list[ConversationPayload] = []

    def _walk(node: JSONValue, inherited: JSONDict | None = None) -> None:
        inherited_metadata: JSONDict = dict(inherited or {})

        if isinstance(node, dict):
            # Direct conversation structure
            messages = node.get("messages")
            if isinstance(messages, list):
                metadata = {
                    key: value
                    for key, value in node.items()
                    if key not in {"messages", "conversations"}
                }
                metadata = {**inherited_metadata, **metadata}
                message_payloads: list[MessagePayload] = [
                    message for message in messages if isinstance(message, dict)
                ]
                if len(message_payloads) != len(messages):
                    raise IngestionError("Conversation messages must be objects")
                conversations.append(
                    ConversationPayload(
                        metadata=metadata,
                        messages=message_payloads,
                    ),
                )

            # Nested conversations list
            nested_conversations = node.get("conversations")
            if isinstance(nested_conversations, list):
                parent_meta = {
                    key: value for key, value in node.items() if key != "conversations"
                }
                parent_meta = {**inherited_metadata, **parent_meta}
                for child in nested_conversations:
                    _walk(child, parent_meta)
            else:
                for value in node.values():
                    if isinstance(value, dict | list):
                        _walk(value, inherited_metadata)

        elif isinstance(node, list):
            for item in node:
                _walk(item, inherited_metadata)

    _walk(payload)
    return conversations


def _resolve_conversation_id(metadata: JSONDict) -> uuid.UUID:
    source_id = metadata.get("source_id") or metadata.get("sourceId")
    if isinstance(source_id, str) and source_id:
        return uuid.uuid5(uuid.NAMESPACE_URL, source_id)
    return uuid.uuid4()


def _parse_timestamp(value: JSONValue) -> datetime:
    if not value:
        return datetime.now(UTC)

    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)

    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(UTC)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
