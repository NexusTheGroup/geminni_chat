"""Add performance-oriented indexes."""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20240306_03"
down_revision = "20240306_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "idx_raw_data_source_type_status",
        "raw_data",
        ["source_type", "status"],
    )
    op.create_index(
        "idx_conversation_turns_raw_data_turn_index",
        "conversation_turns",
        ["raw_data_id", "turn_index"],
    )
    op.create_index(
        "idx_correlation_candidates_raw_status",
        "correlation_candidates",
        ["raw_data_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_correlation_candidates_raw_status",
        table_name="correlation_candidates",
    )
    op.drop_index(
        "idx_conversation_turns_raw_data_turn_index",
        table_name="conversation_turns",
    )
    op.drop_index(
        "idx_raw_data_source_type_status",
        table_name="raw_data",
    )
