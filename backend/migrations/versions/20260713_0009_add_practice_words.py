"""Add practice words to Maimemo sync snapshots and vocabulary profiles.

Revision ID: 20260713_0009
Revises: 20260713_0008
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260713_0009"
down_revision: str | Sequence[str] | None = "20260713_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for table_name in ("maimemo_sync_snapshots", "vocabulary_profiles"):
        op.add_column(
            table_name,
            sa.Column(
                "practice_words",
                sa.JSON(),
                nullable=False,
                server_default="[]",
            ),
        )


def downgrade() -> None:
    for table_name in ("vocabulary_profiles", "maimemo_sync_snapshots"):
        op.drop_column(table_name, "practice_words")