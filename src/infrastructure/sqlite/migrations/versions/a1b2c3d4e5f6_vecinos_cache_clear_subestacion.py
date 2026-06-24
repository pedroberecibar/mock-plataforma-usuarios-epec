# ruff: noqa
"""vecinos_cache: limpiar cache radio-based al migrar a criterio subestación

Revision ID: a1b2c3d4e5f6
Revises: f8a9b0c1d2e3
Create Date: 2026-06-24 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f8a9b0c1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Elimina entradas cacheadas con criterio radio-geográfico; el nuevo criterio
    es subestación (GEOREF.VW_INTELIGENTES) y los resultados son incompatibles."""
    op.execute("DELETE FROM vecinos_cache")


def downgrade() -> None:
    pass
