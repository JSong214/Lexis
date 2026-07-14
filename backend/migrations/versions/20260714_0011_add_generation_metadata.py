"""Add generation metadata to context lessons.

Revision ID: 20260714_0011
Revises: 20260714_0010
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0011"
down_revision: str | Sequence[str] | None = "20260714_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "context_lessons",
        sa.Column(
            "generation_metadata",
            sa.JSON(),
            nullable=False,
            server_default="{}",
        ),
    )


def downgrade() -> None:
    op.drop_column("context_lessons", "generation_metadata")
