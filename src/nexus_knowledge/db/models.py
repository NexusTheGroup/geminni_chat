"""SQLAlchemy ORM models mirroring `docs/DB_SCHEMA.sql`."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import GUID, Base, JSONBType


def default_dict() -> dict[str, Any]:
    """Return a new dictionary. Helps avoid mutable default arguments."""
    return {}


class RawData(Base):
    """Stores raw ingested conversation data."""

    __tablename__ = "raw_data"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONBType(),
        default=default_dict,
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), default="INGESTED")


class ConversationTurn(Base):
    """Normalized conversation turns tied back to the raw payload."""

    __tablename__ = "conversation_turns"
    __table_args__ = (UniqueConstraint("conversation_id", "turn_index"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    raw_data_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("raw_data.id", ondelete="SET NULL"),
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONBType(),
        default=default_dict,
    )


class Entity(Base):
    """Entities extracted during analysis."""

    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    conversation_turn_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("conversation_turns.id", ondelete="CASCADE"),
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[str | None] = mapped_column(String(20))
    relevance: Mapped[float | None] = mapped_column(Float)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONBType(),
        default=default_dict,
    )


class Relationship(Base):
    """Links between entities for correlation and pairing."""

    __tablename__ = "relationships"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("entities.id", ondelete="CASCADE"),
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("entities.id", ondelete="CASCADE"),
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    strength: Mapped[float | None] = mapped_column(Float)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONBType(),
        default=default_dict,
    )


class CorrelationCandidate(Base):
    """Stores potential relationships awaiting confirmation."""

    __tablename__ = "correlation_candidates"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    raw_data_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("raw_data.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONBType(),
        default=default_dict,
    )


class UserFeedback(Base):
    """Stores user feedback submitted through the API."""

    __tablename__ = "user_feedback"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(GUID())
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), default="NEW")


class MLflowRun(Base):
    """Simplified mirror of MLflow run metadata for local queries."""

    __tablename__ = "mlflow_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    experiment_id: Mapped[str] = mapped_column(String(255), nullable=False)
    run_name: Mapped[str | None] = mapped_column(String(255))
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str | None] = mapped_column(String(50))
    params: Mapped[dict[str, Any]] = mapped_column(JSONBType(), default=default_dict)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONBType(), default=default_dict)
    artifacts_uri: Mapped[str | None] = mapped_column(Text)


class DVCDataAsset(Base):
    """Metadata store for DVC-versioned assets."""

    __tablename__ = "dvc_data_assets"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    asset_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    latest_version: Mapped[str | None] = mapped_column(String(255))
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONBType(),
        default=default_dict,
    )
