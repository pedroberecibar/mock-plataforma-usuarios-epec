# ruff: noqa
"""usuarios: tabla de usuarios registrados con su suministro_id

Revision ID: a3f1d2e4b5c6
Revises: f4c8a84fc86c
Create Date: 2026-06-18 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3f1d2e4b5c6"
down_revision: Union[str, Sequence[str], None] = "f4c8a84fc86c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "usuarios",
        sa.Column("usuario", sa.String(), nullable=False),
        sa.Column("suministro_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("usuario"),
    )
    # Seed de desarrollo: usuario demo → suministro real de Oracle
    op.execute("INSERT INTO usuarios (usuario, suministro_id) VALUES ('demo', '2817670')")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("usuarios")
