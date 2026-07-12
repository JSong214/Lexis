"""Create Maimemo connection, sync snapshot, and vocabulary profile.

Revision ID: 20260711_0002
Revises: 20260711_0001
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260711_0002"
down_revision: str | Sequence[str] | None = "20260711_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "maimemo_connections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("encrypted_secret", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_maimemo_connections_user_id"),
        "maimemo_connections",
        ["user_id"],
        unique=True,
    )
    op.create_table(
        "maimemo_sync_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("connection_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("new_words", sa.JSON(), nullable=False),
        sa.Column("fuzzy_words", sa.JSON(), nullable=False),
        sa.Column("mastered_words_sample", sa.JSON(), nullable=False),
        sa.Column("mastered_word_count", sa.Integer(), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["maimemo_connections.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_maimemo_sync_snapshots_connection_id"),
        "maimemo_sync_snapshots",
        ["connection_id"],
    )
    op.create_index(
        op.f("ix_maimemo_sync_snapshots_user_id"),
        "maimemo_sync_snapshots",
        ["user_id"],
    )
    op.create_table(
        "vocabulary_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("new_words", sa.JSON(), nullable=False),
        sa.Column("fuzzy_words", sa.JSON(), nullable=False),
        sa.Column("mastered_words_sample", sa.JSON(), nullable=False),
        sa.Column("mastered_word_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["maimemo_sync_snapshots.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_vocabulary_profiles_snapshot_id"),
        "vocabulary_profiles",
        ["snapshot_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_vocabulary_profiles_user_id"),
        "vocabulary_profiles",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_vocabulary_profiles_user_id"), table_name="vocabulary_profiles")
    op.drop_index(op.f("ix_vocabulary_profiles_snapshot_id"), table_name="vocabulary_profiles")
    op.drop_table("vocabulary_profiles")
    op.drop_index(
        op.f("ix_maimemo_sync_snapshots_user_id"),
        table_name="maimemo_sync_snapshots",
    )
    op.drop_index(
        op.f("ix_maimemo_sync_snapshots_connection_id"),
        table_name="maimemo_sync_snapshots",
    )
    op.drop_table("maimemo_sync_snapshots")
    op.drop_index(op.f("ix_maimemo_connections_user_id"), table_name="maimemo_connections")
    op.drop_table("maimemo_connections")
