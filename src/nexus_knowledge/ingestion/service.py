"""Ingestion pipeline for storing and normalizing conversation data."""

from __future__ import annotations

import json
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from nexus_knowledge.db.models import ConversationTurn
from nexus_knowledge.db.repository import (
    create_conversation_turns,
    create_raw_data,
    get_raw_data,
    update_raw_data_status,
)
from sqlalchemy.orm import Session


class IngestionError(RuntimeError):
    """Raised when ingestion or normalization fails."""


@dataclass
class ConversationPayload:
    """Flattened representation of a conversation ready for normalization."""

    metadata: dict[str, Any]
    messages: list[dict[str, Any]]


def ingest_raw_payload(
    session: Session,
    *,
    source_type: str,
    content: Any,
    metadata: dict[str, Any] | None = None,
    source_id: str | None = None,
) -> uuid.UUID:
    """Persist raw ingestion payload and return its identifier."""
    serialized = (
        content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
    )
    metadata_payload = dict(metadata or {})
    if source_id:
        metadata_payload.setdefault("source_id", source_id)

    record = create_raw_data(
        session,
        source_type=source_type,
        content=serialized,
        source_id=source_id,
        metadata=metadata_payload,
    )
    return record.id


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
        source_platform = conversation.metadata.get(
            "source_platform",
        ) or conversation.metadata.get("sourcePlatform")
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
        session, record_id, status="NORMALIZED", processed_at=datetime.now(UTC),
    )
    return len(turns)


def _flatten_conversations(payload: Any) -> Sequence[ConversationPayload]:
    """Extract conversations + messages from heterogeneous payloads."""
    conversations: list[ConversationPayload] = []

    def _walk(node: Any, inherited: dict[str, Any] | None = None) -> None:
        inherited_metadata = dict(inherited or {})

        if isinstance(node, dict):
            # Direct conversation structure
            if isinstance(node.get("messages"), list):
                metadata = {
                    key: value
                    for key, value in node.items()
                    if key not in {"messages", "conversations"}
                }
                metadata = {**inherited_metadata, **metadata}
                conversations.append(
                    ConversationPayload(
                        metadata=metadata, messages=list(node["messages"]),
                    ),
                )

            # Nested conversations list
            if isinstance(node.get("conversations"), list):
                parent_meta = {
                    key: value for key, value in node.items() if key != "conversations"
                }
                parent_meta = {**inherited_metadata, **parent_meta}
                for child in node["conversations"]:
                    _walk(child, parent_meta)
            else:
                for value in node.values():
                    if isinstance(value, (dict, list)):
                        _walk(value, inherited_metadata)

        elif isinstance(node, list):
            for item in node:
                _walk(item, inherited_metadata)

    _walk(payload)
    return conversations


def _resolve_conversation_id(metadata: dict[str, Any]) -> uuid.UUID:
    source_id = metadata.get("source_id") or metadata.get("sourceId")
    if isinstance(source_id, str) and source_id:
        return uuid.uuid5(uuid.NAMESPACE_URL, source_id)
    return uuid.uuid4()


def _parse_timestamp(value: Any) -> datetime:
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
