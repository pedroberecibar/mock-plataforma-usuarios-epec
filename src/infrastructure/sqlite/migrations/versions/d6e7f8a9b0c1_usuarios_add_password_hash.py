# ruff: noqa
"""usuarios: agrega columna password_hash

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-06-18 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d6e7f8a9b0c1"
down_revision: Union[str, Sequence[str], None] = "c5d6e7f8a9b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Hash argon2id de la contraseña de demo ("demo1234") — solo para entorno de desarrollo.
_DEMO_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4"
    "$37mS9HC0FDK69Cc+xSb4BA"
    "$fZiTgC+tl14T9cpiiwWEYx4c4aa8t0gc55P6kccDUyo"
)


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.add_column(sa.Column("password_hash", sa.String(), nullable=True))
    op.execute(
        f"UPDATE usuarios SET password_hash = '{_DEMO_PASSWORD_HASH}' WHERE usuario = 'demo'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_column("password_hash")
