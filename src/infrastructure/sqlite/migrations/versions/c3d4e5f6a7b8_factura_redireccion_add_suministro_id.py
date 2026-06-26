# ruff: noqa
"""factura_redireccion: add suministro_id para cache de cliente/contrato por suministro

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-26 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "factura_redireccion",
        sa.Column("suministro_id", sa.String(), nullable=True),
    )
    op.create_index(
        "ix_factura_redireccion_suministro_id",
        "factura_redireccion",
        ["suministro_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_factura_redireccion_suministro_id", table_name="factura_redireccion")
    op.drop_column("factura_redireccion", "suministro_id")
