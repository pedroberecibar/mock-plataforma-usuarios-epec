# ruff: noqa
"""cuenta_datos_sensibles: PII cifrada por suministro

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-26 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cuenta_datos_sensibles",
        sa.Column("suministro_id", sa.String(), nullable=False),
        sa.Column("nro_documento_enc", sa.String(), nullable=True),
        sa.Column("cuit_enc", sa.String(), nullable=True),
        sa.Column("actualizado_en", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("suministro_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("cuenta_datos_sensibles")
