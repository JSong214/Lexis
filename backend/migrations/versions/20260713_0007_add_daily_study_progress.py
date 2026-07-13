"""Add daily Maimemo study progress.

Revision ID: 20260713_0007
Revises: 20260713_0006
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260713_0007"
down_revision: str | Sequence[str] | None = "20260713_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def add_progress_columns(table_name: str) -> None:
    for column_name in (
        "daily_finished_count",
        "daily_total_count",
        "daily_study_time_ms",
    ):
        op.add_column(
            table_name,
            sa.Column(
                column_name,
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )


def upgrade() -> None:
    add_progress_columns("maimemo_sync_snapshots")
    add_progress_columns("vocabulary_profiles")


def downgrade() -> None:
    for table_name in ("vocabulary_profiles", "maimemo_sync_snapshots"):
        op.drop_column(table_name, "daily_study_time_ms")
        op.drop_column(table_name, "daily_total_count")
        op.drop_column(table_name, "daily_finished_count")
