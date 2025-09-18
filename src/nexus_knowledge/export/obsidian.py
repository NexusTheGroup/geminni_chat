"""Export analyzed data to Obsidian-compatible Markdown files."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

from nexus_knowledge.db.models import ConversationTurn, Relationship
from nexus_knowledge.db.repository import (
    get_raw_data,
    list_entities_for_raw,
    list_relationships_for_raw,
    list_turns_for_raw,
)
from sqlalchemy.orm import Session


class ExportError(RuntimeError):
    """Raised when the export pipeline cannot complete."""


def export_to_obsidian(
    session: Session, raw_data_id, export_path: str | Path,
) -> list[Path]:
    """Export conversations related to the raw payload into Markdown files."""
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise ExportError(f"raw_data {raw_data_id} not found")

    turns = list_turns_for_raw(session, raw_data_id)
    if not turns:
        raise ExportError("No normalized conversation turns to export")

    entities = list_entities_for_raw(session, raw_data_id)
    relationships = list_relationships_for_raw(session, raw_data_id)

    turn_id_to_conversation_id = {
        str(turn.id): str(turn.conversation_id) for turn in turns
    }
    entity_conversation_map = {
        str(entity.id): turn_id_to_conversation_id.get(str(entity.conversation_turn_id))
        for entity in entities
    }

    export_dir = Path(export_path)
    export_dir.mkdir(parents=True, exist_ok=True)

    turns_by_conversation: dict[str, list[ConversationTurn]] = defaultdict(list)
    for turn in turns:
        turns_by_conversation[str(turn.conversation_id)].append(turn)

    sentiments_by_turn: dict[str, list[str]] = defaultdict(list)
    for entity in entities:
        sentiments_by_turn[str(entity.conversation_turn_id)].append(entity.value)

    relationships_by_conversation: dict[str, list[Relationship]] = defaultdict(list)
    for relationship in relationships:
        source_conv = entity_conversation_map.get(str(relationship.source_entity_id))
        target_conv = entity_conversation_map.get(str(relationship.target_entity_id))
        conversation_id = source_conv or target_conv
        if conversation_id:
            relationships_by_conversation[conversation_id].append(relationship)

    written_files: list[Path] = []
    for conversation_id, conversation_turns in turns_by_conversation.items():
        conversation_turns.sort(key=lambda turn: turn.turn_index)
        file_path = export_dir / f"conversation-{conversation_id}.md"
        front_matter = _build_front_matter(
            source_type=record.source_type,
            raw_data_id=raw_data_id,
            conversation_id=conversation_id,
            conversation_turns=conversation_turns,
            sentiments_by_turn=sentiments_by_turn,
            relationships=relationships_by_conversation.get(conversation_id, []),
        )
        body = _build_body(conversation_turns, sentiments_by_turn)
        file_path.write_text(front_matter + "\n" + body, encoding="utf-8")
        written_files.append(file_path)

    return written_files


def _build_front_matter(
    *,
    source_type: str,
    raw_data_id,
    conversation_id: str,
    conversation_turns: Iterable[ConversationTurn],
    sentiments_by_turn: dict[str, list[str]],
    relationships: Iterable[Relationship],
) -> str:
    sentiment_counts = Counter()
    for turn in conversation_turns:
        sentiment_counts.update(sentiments_by_turn.get(str(turn.id), []))

    relationships_payload = [
        {
            "relationship_id": str(rel.id),
            "type": rel.type,
            "strength": rel.strength,
        }
        for rel in relationships
    ]

    front_matter_lines = [
        "---",
        f"raw_data_id: {raw_data_id}",
        f"conversation_id: {conversation_id}",
        f"source_type: {source_type}",
    ]

    if sentiment_counts:
        front_matter_lines.append("sentiment_summary:")
        for sentiment, count in sentiment_counts.items():
            front_matter_lines.append(f"  {sentiment.lower()}: {count}")
    else:
        front_matter_lines.append("sentiment_summary: {}")

    if relationships_payload:
        front_matter_lines.append("relationships:")
        for rel in relationships_payload:
            front_matter_lines.append("  -")
            front_matter_lines.append(f"    relationship_id: {rel['relationship_id']}")
            front_matter_lines.append(f"    type: {rel['type']}")
            if rel["strength"] is not None:
                front_matter_lines.append(f"    strength: {rel['strength']}")
    else:
        front_matter_lines.append("relationships: []")

    front_matter_lines.append("---")
    return "\n".join(front_matter_lines)


def _build_body(
    conversation_turns: list[ConversationTurn], sentiments_by_turn: dict[str, list[str]],
) -> str:
    lines = [f"# Conversation {conversation_turns[0].conversation_id}"]
    for turn in conversation_turns:
        sentiments = ", ".join(sentiments_by_turn.get(str(turn.id), []))
        sentiment_suffix = f" (sentiment: {sentiments})" if sentiments else ""
        lines.append(
            f"- **{turn.turn_index:02d} {turn.speaker}:** {turn.text}{sentiment_suffix}",
        )
    return "\n".join(lines)
