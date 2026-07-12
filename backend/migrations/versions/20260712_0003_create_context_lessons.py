"""Create context lessons.

Revision ID: 20260712_0003
Revises: 20260711_0002
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0003"
down_revision: str | Sequence[str] | None = "20260711_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "context_lessons",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("cefr_level", sa.String(length=2), nullable=False),
        sa.Column("exam_goal", sa.String(length=120), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("validation_errors", sa.JSON(), nullable=False),
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
        op.f("ix_context_lessons_snapshot_id"),
        "context_lessons",
        ["snapshot_id"],
    )
    op.create_index(
        op.f("ix_context_lessons_status"),
        "context_lessons",
        ["status"],
    )
    op.create_index(
        op.f("ix_context_lessons_user_id"),
        "context_lessons",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_context_lessons_user_id"), table_name="context_lessons")
    op.drop_index(op.f("ix_context_lessons_status"), table_name="context_lessons")
    op.drop_index(op.f("ix_context_lessons_snapshot_id"), table_name="context_lessons")
    op.drop_table("context_lessons")
