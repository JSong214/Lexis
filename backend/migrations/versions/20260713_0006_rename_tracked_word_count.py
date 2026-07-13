"""Rename mastered word count to tracked word count.

Revision ID: 20260713_0006
Revises: 20260712_0005
Create Date: 2026-07-13
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260713_0006"
down_revision: str | Sequence[str] | None = "20260712_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "maimemo_sync_snapshots",
        "mastered_word_count",
        new_column_name="tracked_word_count",
    )
    op.alter_column(
        "vocabulary_profiles",
        "mastered_word_count",
        new_column_name="tracked_word_count",
    )


def downgrade() -> None:
    op.alter_column(
        "vocabulary_profiles",
        "tracked_word_count",
        new_column_name="mastered_word_count",
    )
    op.alter_column(
        "maimemo_sync_snapshots",
        "tracked_word_count",
        new_column_name="mastered_word_count",
    )
