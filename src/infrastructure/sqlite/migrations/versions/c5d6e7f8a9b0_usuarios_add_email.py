# ruff: noqa
"""usuarios: agrega columna email (nullable)

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
Create Date: 2026-06-18 00:02:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c5d6e7f8a9b0"
down_revision: Union[str, Sequence[str], None] = "b4c5d6e7f8a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(), nullable=True))
    # Actualiza el seed de desarrollo con el email del usuario demo
    op.execute("UPDATE usuarios SET email = 'berecibarpedro23@gmail.com' WHERE usuario = 'demo'")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_column("email")
