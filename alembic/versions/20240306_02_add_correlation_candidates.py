"""Add correlation candidates table."""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op
from nexus_knowledge.db.base import GUID, JSONBType

# revision identifiers.
revision = "20240306_02"
down_revision = "20240306_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    metadata_default = sa.text("'{}'::jsonb") if is_postgres else sa.text("'{}'")

    op.create_table(
        "correlation_candidates",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "raw_data_id",
            GUID(),
            sa.ForeignKey("raw_data.id", ondelete="CASCADE"),
            nullable=False,
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
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "metadata",
            JSONBType(),
            nullable=False,
            server_default=metadata_default,
        ),
    )
    op.create_index(
        "idx_correlation_candidates_raw_data",
        "correlation_candidates",
        ["raw_data_id"],
    )
    op.create_index(
        "idx_correlation_candidates_status",
        "correlation_candidates",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_correlation_candidates_status",
        table_name="correlation_candidates",
    )
    op.drop_index(
        "idx_correlation_candidates_raw_data",
        table_name="correlation_candidates",
    )
    op.drop_table("correlation_candidates")
