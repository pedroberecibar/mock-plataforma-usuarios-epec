# ruff: noqa
"""notificaciones_enviadas: deduplicación de alertas por día

Revision ID: b4c5d6e7f8a9
Revises: a3f1d2e4b5c6
Create Date: 2026-06-18 00:01:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4c5d6e7f8a9"
down_revision: Union[str, Sequence[str], None] = "a3f1d2e4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notificaciones_enviadas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("suministro_id", sa.String(), nullable=False),
        sa.Column("tipo_alerta", sa.String(), nullable=False),
        sa.Column("fecha_envio", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # Índice único por (suministro_id, tipo_alerta, día) para deduplicación diaria
    op.execute(
        "CREATE UNIQUE INDEX uq_notif_enviada_dia "
        "ON notificaciones_enviadas(suministro_id, tipo_alerta, DATE(fecha_envio))"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_notif_enviada_dia", table_name="notificaciones_enviadas")
    op.drop_table("notificaciones_enviadas")
