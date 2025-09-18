"""Analysis pipeline that processes normalized conversations."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import mlflow
from sqlalchemy.orm import Session

from nexus_knowledge.analysis.model import HeuristicSentimentModel
from nexus_knowledge.db.models import Entity
from nexus_knowledge.db.repository import (
    create_entities,
    get_raw_data,
    iter_turns_for_raw,
    update_raw_data_status,
)
from nexus_knowledge.mlflow_utils import configure_mlflow


class AnalysisError(RuntimeError):
    """Raised when the analysis pipeline cannot proceed."""


def run_analysis_for_raw_data(session: Session, raw_data_id: uuid.UUID) -> int:
    """Analyze normalized conversation turns and persist sentiment entities."""
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise AnalysisError(f"raw_data {raw_data_id} not found")

    model = HeuristicSentimentModel()

    configure_mlflow()
    mlflow.set_experiment("Analysis")

    turn_iterator = iter_turns_for_raw(session, raw_data_id=raw_data_id, chunk_size=200)
    positive = negative = neutral = 0
    processed = 0
    batch: list[Entity] = []
    batch_size = 100

    with mlflow.start_run(run_name=f"analysis-{raw_data_id}", nested=True):
        mlflow.log_params(
            {
                "raw_data_id": str(raw_data_id),
                "source_type": record.source_type,
            },
        )

        for turn in turn_iterator:
            processed += 1
            sentiment = model.predict(turn.text)
            if sentiment.label == "POSITIVE":
                positive += 1
            elif sentiment.label == "NEGATIVE":
                negative += 1
            else:
                neutral += 1

            batch.append(
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

            if len(batch) >= batch_size:
                create_entities(session, batch)
                batch.clear()

        if processed == 0:
            mlflow.log_params({"turn_count": 0})
            update_raw_data_status(session, raw_data_id, status="ANALYSIS_FAILED")
            raise AnalysisError("No normalized turns available for analysis")

        if batch:
            create_entities(session, batch)

        mlflow.log_params({"turn_count": processed})
        mlflow.log_metrics(
            {
                "positive_ratio": positive / processed,
                "negative_ratio": negative / processed,
                "neutral_ratio": neutral / processed,
            },
        )

    update_raw_data_status(
        session,
        raw_data_id,
        status="ANALYZED",
        processed_at=datetime.now(UTC),
    )
    return processed
