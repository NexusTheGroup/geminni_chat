"""Correlation candidate generation pipeline."""

from __future__ import annotations

import itertools
import uuid
from datetime import UTC, datetime

from nexus_knowledge.db.models import CorrelationCandidate, Relationship
from nexus_knowledge.db.repository import (
    create_correlation_candidates,
    create_relationships,
    get_raw_data,
    iter_turns_for_raw,
    list_correlation_candidates,
    list_entities_for_raw,
    list_relationships_for_raw,
    update_candidate_status,
    update_raw_data_status,
)
from sqlalchemy.orm import Session


class CorrelationError(RuntimeError):
    """Raised when correlation generation cannot complete."""


def _pair_key(entity_a: uuid.UUID, entity_b: uuid.UUID) -> tuple[uuid.UUID, uuid.UUID]:
    return tuple(sorted((entity_a, entity_b)))  # type: ignore[return-value]


def generate_candidates_for_raw(
    session: Session,
    raw_data_id: uuid.UUID,
    *,
    min_score: float = 0.05,
) -> int:
    """Produce correlation candidates from analyzed entities."""
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise CorrelationError(f"raw_data {raw_data_id} not found")

    entities = [
        entity
        for entity in list_entities_for_raw(session, raw_data_id)
        if entity.type == "SENTIMENT"
    ]
    if not entities:
        update_raw_data_status(session, raw_data_id, status="CORRELATION_SKIPPED")
        raise CorrelationError("No sentiment entities available for correlation")

    turns = {
        turn.id: turn for turn in iter_turns_for_raw(session, raw_data_id=raw_data_id)
    }
    if not turns:
        update_raw_data_status(session, raw_data_id, status="CORRELATION_SKIPPED")
        raise CorrelationError("No normalized turns available for correlation")

    existing_pairs = {
        _pair_key(candidate.source_entity_id, candidate.target_entity_id)
        for candidate in list_correlation_candidates(
            session,
            raw_data_id,
            order_by_score=False,
        )
    }

    new_candidates: list[CorrelationCandidate] = []

    for entity_a, entity_b in itertools.combinations(entities, 2):
        if entity_a.value != entity_b.value:
            continue

        pair = _pair_key(entity_a.id, entity_b.id)
        if pair in existing_pairs:
            continue

        turn_a = turns.get(entity_a.conversation_turn_id)
        turn_b = turns.get(entity_b.conversation_turn_id)
        if turn_a is None or turn_b is None:
            continue

        score = _compute_score(entity_a.relevance or 0.0, entity_b.relevance or 0.0)
        if score < min_score:
            continue

        rationale = (
            f"Both turns share {entity_a.value} sentiment in conversations "
            f"{turn_a.conversation_id} and {turn_b.conversation_id}."
        )
        metadata = {
            "turn_a": str(turn_a.conversation_id),
            "turn_b": str(turn_b.conversation_id),
            "sentiment": entity_a.value,
        }

        new_candidates.append(
            CorrelationCandidate(
                raw_data_id=raw_data_id,
                source_entity_id=entity_a.id,
                target_entity_id=entity_b.id,
                score=score,
                rationale=rationale,
                metadata_=metadata,
            ),
        )
        existing_pairs.add(pair)

    create_correlation_candidates(session, new_candidates)
    update_raw_data_status(
        session,
        raw_data_id,
        status="CORRELATION_GENERATED",
        processed_at=datetime.now(UTC),
    )
    return len(new_candidates)


def _compute_score(relevance_a: float, relevance_b: float) -> float:
    diff = abs(relevance_a - relevance_b)
    return max(0.0, 1.0 - min(diff, 1.0))


def fuse_candidates_for_raw(
    session: Session,
    raw_data_id: uuid.UUID,
    *,
    min_score: float = 0.2,
) -> dict[str, int]:
    """Fuse correlation candidates into confirmed relationships."""
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise CorrelationError(f"raw_data {raw_data_id} not found")

    pending_candidates = list_correlation_candidates(
        session,
        raw_data_id,
        status="PENDING",
    )
    if not pending_candidates:
        return {"confirmed": 0, "rejected": 0}

    confirmed: list[Relationship] = []
    confirm_ids: list[uuid.UUID] = []
    reject_ids: list[uuid.UUID] = []

    for candidate in pending_candidates:
        if candidate.score >= min_score:
            confirmed.append(
                Relationship(
                    source_entity_id=candidate.source_entity_id,
                    target_entity_id=candidate.target_entity_id,
                    type="SENTIMENT_LINK",
                    strength=candidate.score,
                    metadata_={
                        "raw_data_id": str(candidate.raw_data_id),
                        "rationale": candidate.rationale,
                    },
                ),
            )
            confirm_ids.append(candidate.id)
        else:
            reject_ids.append(candidate.id)

    create_relationships(session, confirmed)
    if confirm_ids:
        update_candidate_status(session, confirm_ids, "CONFIRMED")
    if reject_ids:
        update_candidate_status(session, reject_ids, "REJECTED")

    if confirmed:
        update_raw_data_status(
            session,
            raw_data_id,
            status="CORRELATED",
            processed_at=datetime.now(UTC),
        )
    elif not list_relationships_for_raw(session, raw_data_id):
        update_raw_data_status(session, raw_data_id, status="CORRELATION_REVIEWED")

    return {"confirmed": len(confirm_ids), "rejected": len(reject_ids)}
