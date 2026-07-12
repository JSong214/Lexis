"""Create context mastery states.

Revision ID: 20260712_0005
Revises: 20260712_0004
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0005"
down_revision: str | Sequence[str] | None = "20260712_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "lesson_attempts",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "context_mastery_states",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("word", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("exposure_count", sa.Integer(), nullable=False),
        sa.Column("successful_attempts", sa.Integer(), nullable=False),
        sa.Column("last_lesson_id", sa.Uuid(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["last_lesson_id"],
            ["context_lessons.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "word"),
    )
    op.create_index(
        op.f("ix_context_mastery_states_user_id"),
        "context_mastery_states",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_context_mastery_states_user_id"),
        table_name="context_mastery_states",
    )
    op.drop_table("context_mastery_states")
    op.drop_column("lesson_attempts", "completed_at")
