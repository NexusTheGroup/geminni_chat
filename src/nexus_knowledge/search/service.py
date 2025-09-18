"""Hybrid keyword + pseudo-semantic search across conversation turns."""

from __future__ import annotations

import re

from nexus_knowledge.db.models import ConversationTurn, Entity
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

TOKEN_PATTERN = re.compile(r"[\w']+")
SNIPPET_MAX_LENGTH = 200


class SearchError(RuntimeError):
    """Raised when search cannot be executed."""


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def _semantic_score(query_tokens: list[str], text_tokens: list[str]) -> float:
    if not query_tokens or not text_tokens:
        return 0.0
    query_set = set(query_tokens)
    text_set = set(text_tokens)
    overlap = len(query_set & text_set)
    union = len(query_set | text_set)
    if union == 0:
        return 0.0
    return overlap / union


def hybrid_search(
    session: Session,
    query: str,
    *,
    limit: int = 10,
) -> list[dict[str, object]]:
    """Return ranked conversation turns using keyword + semantic heuristics."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        raise SearchError("Query must contain at least one alphanumeric token")

    like_filters = [ConversationTurn.text.ilike(f"%{token}%") for token in query_tokens]
    stmt = (
        select(ConversationTurn)
        .where(or_(*like_filters))
        .order_by(ConversationTurn.timestamp.desc())
        .limit(limit * 5)
    )
    candidate_turns = session.scalars(stmt).all()

    if not candidate_turns:
        return []

    sentiments: dict[str, str] = {}
    entity_stmt = select(Entity).where(
        Entity.type == "SENTIMENT",
        Entity.conversation_turn_id.in_([turn.id for turn in candidate_turns]),
    )
    for entity in session.scalars(entity_stmt):
        sentiments[str(entity.conversation_turn_id)] = entity.value

    scored_results: list[tuple[float, ConversationTurn, list[str]]] = []
    for turn in candidate_turns:
        text_tokens = _tokenize(turn.text)
        if not text_tokens:
            continue
        keyword_matches = sum(1 for token in query_tokens if token in text_tokens)
        keyword_score = keyword_matches / len(query_tokens)
        semantic_score = _semantic_score(query_tokens, text_tokens)
        score = (keyword_score * 0.7) + (semantic_score * 0.3)
        if score <= 0:
            continue
        scored_results.append((score, turn, text_tokens))

    scored_results.sort(key=lambda row: row[0], reverse=True)

    results = []
    for score, turn, _ in scored_results[:limit]:
        snippet = turn.text
        if len(snippet) > SNIPPET_MAX_LENGTH:
            snippet = snippet[: SNIPPET_MAX_LENGTH - 3] + "..."
        results.append(
            {
                "turn_id": str(turn.id),
                "conversation_id": str(turn.conversation_id),
                "turn_index": turn.turn_index,
                "timestamp": turn.timestamp.isoformat(),
                "snippet": snippet,
                "score": round(score, 4),
                "sentiment": sentiments.get(str(turn.id)),
            },
        )

    return results
