"""Initial database schema for NexusKnowledge."""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from nexus_knowledge.db.base import GUID, JSONBType

from alembic import op

# revision identifiers, used by Alembic.
revision = "20240306_01"
down_revision = None
branch_labels = None
depends_on = None


def _uuid_server_default(is_postgres: bool) -> sa.text | None:
    return sa.text("uuid_generate_v4()") if is_postgres else None


def _json_server_default(is_postgres: bool) -> sa.text | None:
    return sa.text("'{}'::jsonb") if is_postgres else sa.text("'{}'")


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    is_postgres = dialect_name == "postgresql"

    if is_postgres:
        op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    op.create_table(
        "raw_data",
        sa.Column(
            "id",
            GUID(),
            primary_key=True,
            default=uuid.uuid4,
            server_default=_uuid_server_default(is_postgres),
        ),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "metadata",
            JSONBType(),
            nullable=False,
            server_default=_json_server_default(is_postgres),
        ),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="INGESTED",
        ),
    )

    op.create_table(
        "conversation_turns",
        sa.Column(
            "id",
            GUID(),
            primary_key=True,
            default=uuid.uuid4,
            server_default=_uuid_server_default(is_postgres),
        ),
        sa.Column(
            "raw_data_id",
            GUID(),
            sa.ForeignKey("raw_data.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("conversation_id", GUID(), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("speaker", sa.String(length=50), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "metadata",
            JSONBType(),
            nullable=False,
            server_default=_json_server_default(is_postgres),
        ),
        sa.UniqueConstraint(
            "conversation_id",
            "turn_index",
            name="uq_conversation_turn",
        ),
    )

    op.create_table(
        "entities",
        sa.Column(
            "id",
            GUID(),
            primary_key=True,
            default=uuid.uuid4,
            server_default=_uuid_server_default(is_postgres),
        ),
        sa.Column(
            "conversation_turn_id",
            GUID(),
            sa.ForeignKey("conversation_turns.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("sentiment", sa.String(length=20), nullable=True),
        sa.Column("relevance", sa.Float(), nullable=True),
        sa.Column(
            "metadata",
            JSONBType(),
            nullable=False,
            server_default=_json_server_default(is_postgres),
        ),
    )

    op.create_table(
        "relationships",
        sa.Column(
            "id",
            GUID(),
            primary_key=True,
            default=uuid.uuid4,
            server_default=_uuid_server_default(is_postgres),
        ),
        sa.Column(
            "source_entity_id",
            GUID(),
            sa.ForeignKey("entities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_entity_id",
            GUID(),
            sa.ForeignKey("entities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("strength", sa.Float(), nullable=True),
        sa.Column(
            "metadata",
            JSONBType(),
            nullable=False,
            server_default=_json_server_default(is_postgres),
        ),
    )

    op.create_table(
        "user_feedback",
        sa.Column(
            "id",
            GUID(),
            primary_key=True,
            default=uuid.uuid4,
            server_default=_uuid_server_default(is_postgres),
        ),
        sa.Column("feedback_type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("user_id", GUID(), nullable=True),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="NEW"),
    )

    op.create_table(
        "mlflow_runs",
        sa.Column(
            "run_id",
            GUID(),
            primary_key=True,
            default=uuid.uuid4,
            server_default=_uuid_server_default(is_postgres),
        ),
        sa.Column("experiment_id", sa.String(length=255), nullable=False),
        sa.Column("run_name", sa.String(length=255), nullable=True),
        sa.Column(
            "start_time",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column(
            "params",
            JSONBType(),
            nullable=False,
            server_default=_json_server_default(is_postgres),
        ),
        sa.Column(
            "metrics",
            JSONBType(),
            nullable=False,
            server_default=_json_server_default(is_postgres),
        ),
        sa.Column("artifacts_uri", sa.Text(), nullable=True),
    )

    op.create_table(
        "dvc_data_assets",
        sa.Column(
            "id",
            GUID(),
            primary_key=True,
            default=uuid.uuid4,
            server_default=_uuid_server_default(is_postgres),
        ),
        sa.Column("asset_name", sa.String(length=255), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("latest_version", sa.String(length=255), nullable=True),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "metadata",
            JSONBType(),
            nullable=False,
            server_default=_json_server_default(is_postgres),
        ),
        sa.UniqueConstraint("asset_name", name="uq_dvc_asset_name"),
    )

    op.create_index("idx_raw_data_source_type", "raw_data", ["source_type"])
    op.create_index("idx_raw_data_status", "raw_data", ["status"])
    op.create_index(
        "idx_conversation_turns_conversation_id",
        "conversation_turns",
        ["conversation_id"],
    )
    op.create_index("idx_entities_type", "entities", ["type"])
    op.create_index("idx_entities_value", "entities", ["value"])
    op.create_index("idx_user_feedback_type", "user_feedback", ["feedback_type"])
    op.create_index("idx_mlflow_runs_experiment_id", "mlflow_runs", ["experiment_id"])


def downgrade() -> None:
    op.drop_index("idx_mlflow_runs_experiment_id", table_name="mlflow_runs")
    op.drop_index("idx_user_feedback_type", table_name="user_feedback")
    op.drop_index("idx_entities_value", table_name="entities")
    op.drop_index("idx_entities_type", table_name="entities")
    op.drop_index(
        "idx_conversation_turns_conversation_id",
        table_name="conversation_turns",
    )
    op.drop_index("idx_raw_data_status", table_name="raw_data")
    op.drop_index("idx_raw_data_source_type", table_name="raw_data")

    op.drop_table("dvc_data_assets")
    op.drop_table("mlflow_runs")
    op.drop_table("user_feedback")
    op.drop_table("relationships")
    op.drop_table("entities")
    op.drop_table("conversation_turns")
    op.drop_table("raw_data")
