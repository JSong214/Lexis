"""Persist vocabulary words with their snapshot source category.

Revision ID: 20260714_0010
Revises: 20260713_0009
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0010"
down_revision: str | Sequence[str] | None = "20260713_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vocabulary_snapshot_words",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("word", sa.String(length=128), nullable=False),
        sa.Column("source_category", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["maimemo_sync_snapshots.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "snapshot_id",
            "word",
            "source_category",
            name="uq_vocabulary_snapshot_word_source",
        ),
    )
    op.create_index(
        op.f("ix_vocabulary_snapshot_words_snapshot_id"),
        "vocabulary_snapshot_words",
        ["snapshot_id"],
    )
    op.create_index(
        op.f("ix_vocabulary_snapshot_words_user_id"),
        "vocabulary_snapshot_words",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_vocabulary_snapshot_words_user_id"),
        table_name="vocabulary_snapshot_words",
    )
    op.drop_index(
        op.f("ix_vocabulary_snapshot_words_snapshot_id"),
        table_name="vocabulary_snapshot_words",
    )
    op.drop_table("vocabulary_snapshot_words")
