"""Add user learning preferences.

Revision ID: 20260713_0008
Revises: 20260713_0007
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260713_0008"
down_revision: str | Sequence[str] | None = "20260713_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "cefr_level",
            sa.String(length=2),
            nullable=False,
            server_default="B2",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "learning_goal",
            sa.String(length=64),
            nullable=False,
            server_default="General English",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "learning_goal")
    op.drop_column("users", "cefr_level")
