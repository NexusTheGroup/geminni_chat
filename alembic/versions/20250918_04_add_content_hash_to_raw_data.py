"""Add content_hash to raw_data.

Revision ID: 20250918_04
Revises: 20240306_03_performance_indexes
Create Date: 2025-09-18 12:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250918_04"
down_revision: str | None = "20240306_03"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "raw_data",
        sa.Column("content_hash", sa.String(length=64), nullable=True),
    )
    op.create_index(
        op.f("ix_raw_data_content_hash"),
        "raw_data",
        ["content_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_raw_data_content_hash"), table_name="raw_data")
    op.drop_column("raw_data", "content_hash")
