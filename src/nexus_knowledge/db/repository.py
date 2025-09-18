"""High-level database operations used across the application."""

from __future__ import annotations

import uuid
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    ConversationTurn,
    CorrelationCandidate,
    Entity,
    RawData,
    Relationship,
    UserFeedback,
)


def create_raw_data(  # noqa: PLR0913
    session: Session,
    *,
    source_type: str,
    content: str,
    source_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    status: str = "INGESTED",
    content_hash: str | None = None,
) -> RawData:
    """Insert a raw_data record and return the persisted instance."""
    record = RawData(
        source_type=source_type,
        content=content,
        source_id=source_id,
        metadata_=metadata or {},
        status=status,
        content_hash=content_hash,
    )
    session.add(record)
    session.flush()
    return record


def get_raw_data(session: Session, record_id: uuid.UUID) -> RawData | None:
    """Fetch a raw_data entry by its identifier."""
    stmt = select(RawData).where(RawData.id == record_id)
    return session.execute(stmt).scalar_one_or_none()


def get_raw_data_by_hash(session: Session, content_hash: str) -> RawData | None:
    """Fetch a raw_data entry by its content hash."""
    stmt = select(RawData).where(RawData.content_hash == content_hash)
    return session.execute(stmt).scalar_one_or_none()


def update_raw_data_status(
    session: Session,
    record_id: uuid.UUID,
    *,
    status: str,
    processed_at: datetime | None = None,
) -> RawData | None:
    """Update the status (and optional processed timestamp) of a raw_data record."""
    record = get_raw_data(session, record_id)
    if record is None:
        return None

    record.status = status
    if processed_at is not None:
        record.processed_at = processed_at
    elif status.upper() == "NORMALIZED":
        record.processed_at = datetime.now(UTC)

    session.flush()
    return record


def create_conversation_turns(
    session: Session,
    turns: Sequence[ConversationTurn],
) -> Sequence[ConversationTurn]:
    """Persist a batch of conversation turns."""
    session.add_all(turns)
    session.flush()
    return turns


def list_conversation_turns(
    session: Session,
    conversation_id: uuid.UUID,
) -> Sequence[ConversationTurn]:
    """Return all conversation turns for a given conversation identifier."""
    return list(
        iter_conversation_turns(
            session,
            conversation_id=conversation_id,
            chunk_size=250,
        ),
    )


def iter_conversation_turns(
    session: Session,
    *,
    conversation_id: uuid.UUID,
    chunk_size: int = 250,
) -> Iterator[ConversationTurn]:
    """Stream conversation turns for the provided conversation identifier."""
    stmt = (
        select(ConversationTurn)
        .where(ConversationTurn.conversation_id == conversation_id)
        .order_by(ConversationTurn.turn_index)
        .execution_options(stream_results=True, yield_per=chunk_size)
    )
    return session.execute(stmt).scalars()


def list_turns_for_raw(
    session: Session,
    raw_data_id: uuid.UUID,
) -> Sequence[ConversationTurn]:
    """Fetch all conversation turns associated with a raw payload."""
    return list(iter_turns_for_raw(session, raw_data_id=raw_data_id))


def iter_turns_for_raw(
    session: Session,
    *,
    raw_data_id: uuid.UUID,
    chunk_size: int = 250,
) -> Iterator[ConversationTurn]:
    """Yield conversation turns for a raw payload in chunks to limit memory pressure."""
    stmt = (
        select(ConversationTurn)
        .where(ConversationTurn.raw_data_id == raw_data_id)
        .order_by(ConversationTurn.conversation_id, ConversationTurn.turn_index)
        .execution_options(stream_results=True, yield_per=chunk_size)
    )
    return session.execute(stmt).scalars()


def create_entities(session: Session, entities: Sequence[Entity]) -> Sequence[Entity]:
    """Persist a batch of entity records."""
    session.add_all(entities)
    session.flush()
    return entities


def list_entities_for_raw(session: Session, raw_data_id: uuid.UUID) -> Sequence[Entity]:
    """Return entities linked to the provided raw payload."""
    stmt = (
        select(Entity)
        .join(ConversationTurn, Entity.conversation_turn_id == ConversationTurn.id)
        .where(ConversationTurn.raw_data_id == raw_data_id)
    )
    return session.scalars(stmt).all()


def create_correlation_candidates(
    session: Session,
    candidates: Sequence[CorrelationCandidate],
) -> Sequence[CorrelationCandidate]:
    """Persist correlation candidates in bulk."""
    if not candidates:
        return []

    session.add_all(candidates)
    session.flush()
    return candidates


def list_correlation_candidates(
    session: Session,
    raw_data_id: uuid.UUID,
    *,
    status: str | None = None,
    limit: int | None = None,
    order_by_score: bool = True,
) -> Sequence[CorrelationCandidate]:
    """Fetch correlation candidates scoped to a raw payload."""
    stmt = select(CorrelationCandidate).where(
        CorrelationCandidate.raw_data_id == raw_data_id,
    )
    if status is not None:
        stmt = stmt.where(CorrelationCandidate.status == status)
    if order_by_score:
        stmt = stmt.order_by(CorrelationCandidate.score.desc())
    if limit is not None:
        stmt = stmt.limit(limit)
    return session.scalars(stmt).all()


def update_candidate_status(
    session: Session,
    candidate_ids: Sequence[uuid.UUID],
    status: str,
) -> None:
    """Bulk update candidate status values."""
    if not candidate_ids:
        return
    stmt = (
        select(CorrelationCandidate)
        .where(CorrelationCandidate.id.in_(candidate_ids))
        .execution_options(populate_existing=True)
    )
    for candidate in session.scalars(stmt):
        candidate.status = status
    session.flush()


def create_relationships(
    session: Session,
    relationships: Sequence[Relationship],
) -> Sequence[Relationship]:
    """Persist relationship records."""
    if not relationships:
        return []

    session.add_all(relationships)
    session.flush()
    return relationships


def list_relationships_for_raw(
    session: Session,
    raw_data_id: uuid.UUID,
) -> Sequence[Relationship]:
    """Return relationships associated with a raw payload via its entities."""
    stmt = (
        select(Relationship)
        .join(Entity, Relationship.source_entity_id == Entity.id)
        .join(ConversationTurn, Entity.conversation_turn_id == ConversationTurn.id)
        .where(ConversationTurn.raw_data_id == raw_data_id)
    )
    return session.scalars(stmt).all()


def create_user_feedback(  # noqa: PLR0913
    session: Session,
    *,
    feedback_id: uuid.UUID,
    feedback_type: str,
    message: str,
    user_id: uuid.UUID | None = None,
    status: str = "NEW",
) -> UserFeedback:
    """Persist a user_feedback record with the provided identifier."""
    record = UserFeedback(
        id=feedback_id,
        feedback_type=feedback_type,
        message=message,
        user_id=user_id,
        status=status,
    )
    session.add(record)
    session.flush()
    return record


def get_user_feedback(
    session: Session,
    feedback_id: uuid.UUID,
) -> UserFeedback | None:
    """Fetch a user_feedback record by its identifier."""
    stmt = select(UserFeedback).where(UserFeedback.id == feedback_id)
    return session.execute(stmt).scalar_one_or_none()


def list_feedback(
    session: Session,
    *,
    status: str | None = None,
    limit: int = 50,
) -> Sequence[UserFeedback]:
    """Return feedback entries optionally filtered by status."""
    stmt = select(UserFeedback).order_by(UserFeedback.submitted_at.desc()).limit(limit)
    if status:
        stmt = stmt.where(UserFeedback.status == status)
    return session.scalars(stmt).all()


def update_feedback_status(
    session: Session,
    feedback_id: uuid.UUID,
    *,
    status: str,
) -> UserFeedback | None:
    """Update the status of a feedback entry."""
    record = get_user_feedback(session, feedback_id)
    if record is None:
        return None
    record.status = status
    session.flush()
    return record
