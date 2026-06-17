# ruff: noqa
"""proyeccion_mensual rango nullable

Revision ID: f4c8a84fc86c
Revises: 44bce45cbd5a
Create Date: 2026-06-17 11:41:44.969015

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4c8a84fc86c"
down_revision: Union[str, Sequence[str], None] = "44bce45cbd5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("proyeccion_mensual") as batch_op:
        batch_op.alter_column(
            "rango_inferior_kwh",
            existing_type=sa.Float(),
            nullable=True,
        )
        batch_op.alter_column(
            "rango_superior_kwh",
            existing_type=sa.Float(),
            nullable=True,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("proyeccion_mensual") as batch_op:
        batch_op.alter_column(
            "rango_superior_kwh",
            existing_type=sa.Float(),
            nullable=False,
        )
        batch_op.alter_column(
            "rango_inferior_kwh",
            existing_type=sa.Float(),
            nullable=False,
        )
