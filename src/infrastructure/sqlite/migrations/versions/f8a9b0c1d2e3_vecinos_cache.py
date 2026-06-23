# ruff: noqa
"""vecinos_cache: tabla de cache TTL para vecinos por suministro

Revision ID: f8a9b0c1d2e3
Revises: e7f8a9b0c1d2
Create Date: 2026-06-22 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f8a9b0c1d2e3"
down_revision: Union[str, Sequence[str], None] = "e7f8a9b0c1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "vecinos_cache",
        sa.Column("suministro_id", sa.String(), nullable=False),
        sa.Column("vecinos_json", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("suministro_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("vecinos_cache")
