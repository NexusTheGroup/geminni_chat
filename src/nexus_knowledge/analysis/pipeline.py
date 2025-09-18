"""Analysis pipeline that processes normalized conversations."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import mlflow
from nexus_knowledge.analysis.model import HeuristicSentimentModel
from nexus_knowledge.db.models import Entity
from nexus_knowledge.db.repository import (
    create_entities,
    get_raw_data,
    list_turns_for_raw,
    update_raw_data_status,
)
from nexus_knowledge.mlflow_utils import configure_mlflow
from sqlalchemy.orm import Session


class AnalysisError(RuntimeError):
    """Raised when the analysis pipeline cannot proceed."""


def run_analysis_for_raw_data(session: Session, raw_data_id: uuid.UUID) -> int:
    """Analyze normalized conversation turns and persist sentiment entities."""
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise AnalysisError(f"raw_data {raw_data_id} not found")

    turns = list_turns_for_raw(session, raw_data_id)
    if not turns:
        update_raw_data_status(session, raw_data_id, status="ANALYSIS_FAILED")
        raise AnalysisError("No normalized turns available for analysis")

    model = HeuristicSentimentModel()

    configure_mlflow()
    mlflow.set_experiment("Analysis")

    with mlflow.start_run(run_name=f"analysis-{raw_data_id}"):
        mlflow.log_params(
            {
                "raw_data_id": str(raw_data_id),
                "source_type": record.source_type,
                "turn_count": len(turns),
            },
        )

        positive = negative = neutral = 0
        entities: list[Entity] = []

        for turn in turns:
            sentiment = model.predict(turn.text)
            if sentiment.label == "POSITIVE":
                positive += 1
            elif sentiment.label == "NEGATIVE":
                negative += 1
            else:
                neutral += 1

            entities.append(
                Entity(
                    conversation_turn_id=turn.id,
                    type="SENTIMENT",
                    value=sentiment.label,
                    sentiment=sentiment.label,
                    relevance=sentiment.score,
                    metadata_={
                        "positive_matches": sentiment.positive_matches,
                        "negative_matches": sentiment.negative_matches,
                    },
                ),
            )

        create_entities(session, entities)

        total_turns = len(turns)
        mlflow.log_metrics(
            {
                "positive_ratio": positive / total_turns,
                "negative_ratio": negative / total_turns,
                "neutral_ratio": neutral / total_turns,
            },
        )

    update_raw_data_status(
        session, raw_data_id, status="ANALYZED", processed_at=datetime.now(UTC),
    )
    return len(entities)
