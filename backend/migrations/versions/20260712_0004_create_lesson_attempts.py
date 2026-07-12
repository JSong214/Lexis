"""Create lesson attempts and exercise feedback.

Revision ID: 20260712_0004
Revises: 20260712_0003
Create Date: 2026-07-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260712_0004"
down_revision: str | Sequence[str] | None = "20260712_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lesson_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("final_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["context_lessons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "lesson_id"),
    )
    op.create_index(
        op.f("ix_lesson_attempts_lesson_id"),
        "lesson_attempts",
        ["lesson_id"],
    )
    op.create_index(
        op.f("ix_lesson_attempts_status"),
        "lesson_attempts",
        ["status"],
    )
    op.create_index(
        op.f("ix_lesson_attempts_user_id"),
        "lesson_attempts",
        ["user_id"],
    )

    op.create_table(
        "exercise_feedback",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("exercise_index", sa.Integer(), nullable=False),
        sa.Column("exercise_type", sa.String(length=32), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("feedback_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["attempt_id"], ["lesson_attempts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id", "exercise_index"),
    )
    op.create_index(
        op.f("ix_exercise_feedback_attempt_id"),
        "exercise_feedback",
        ["attempt_id"],
    )
    op.create_index(
        op.f("ix_exercise_feedback_user_id"),
        "exercise_feedback",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_exercise_feedback_user_id"), table_name="exercise_feedback")
    op.drop_index(op.f("ix_exercise_feedback_attempt_id"), table_name="exercise_feedback")
    op.drop_table("exercise_feedback")
    op.drop_index(op.f("ix_lesson_attempts_user_id"), table_name="lesson_attempts")
    op.drop_index(op.f("ix_lesson_attempts_status"), table_name="lesson_attempts")
    op.drop_index(op.f("ix_lesson_attempts_lesson_id"), table_name="lesson_attempts")
    op.drop_table("lesson_attempts")
