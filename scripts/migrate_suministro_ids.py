"""Migración one-shot: normaliza suministro_ids bare ('2817670') a canónico ('SRV-2817670').

El bulk reader de Oracle almacenaba SRV_CODIGO sin prefijo. Esto generó, para muchos
suministros, filas "gemelas": una bare ('2817670') de la ingesta vieja y una canónica
('SRV-2817670') de la re-ingesta post-fix. La app SIEMPRE lee el canónico (SRV-), por lo
que las filas bare quedan huérfanas (no se leen) pero ocupan espacio y confunden.

Este script consolida todo al formato canónico SRV-:
  - Donde la fila bare NO colisiona con una canónica (PK libre): la renombra a SRV-
    (esto recupera, p.ej., historia más vieja que solo existía en la fila bare).
  - Donde SÍ colisiona (ya existe el gemelo SRV-): descarta la fila bare.
En las fechas solapadas el kWh es idéntico, así que no se pierde información.

Es idempotente: correrlo de nuevo no hace nada (no quedan filas bare).

Uso:
    uv run python scripts/migrate_suministro_ids.py --db data/plataforma_clientes.db [--dry-run]
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# (tabla, columna con el suministro_id). Solo tablas cuya columna referencia un suministro.
_TABLES: list[tuple[str, str]] = [
    ("consumo_diario", "suministro_id"),
    ("consumo_horario", "suministro_id"),
    ("proyeccion_mensual", "suministro_id"),
    ("objetivo_consumo", "suministro_id"),
    ("vecinos_cache", "suministro_id"),
    ("suministros", "id"),  # tabla padre — se migra al final para no romper FKs en cascada
]


def _migrate(db_path: str, dry_run: bool) -> None:
    conn = sqlite3.connect(db_path)
    try:
        # FKs off: renombramos PKs padre e hijas en el mismo batch; el orden las mantiene consistentes.
        conn.execute("PRAGMA foreign_keys = OFF")
        cur = conn.cursor()
        total_renamed = 0
        total_dropped = 0

        for table, col in _TABLES:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cur.fetchone():
                print(f"  [skip] tabla '{table}' no existe")
                continue

            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} NOT LIKE 'SRV-%'")
            (bare,) = cur.fetchone()
            if bare == 0:
                print(f"  {table}.{col}: sin filas bare — OK")
                continue

            if dry_run:
                print(f"  {table}.{col}: {bare} filas bare se consolidarían")
                continue

            # 1. Renombra las que no colisionan con su gemelo canónico (recupera historia única).
            cur.execute(
                f"UPDATE OR IGNORE {table} SET {col} = 'SRV-' || {col} WHERE {col} NOT LIKE 'SRV-%'"
            )
            renamed = cur.rowcount
            # 2. Borra las bare que quedaron (colisionaban con un gemelo SRV- ya existente).
            cur.execute(f"DELETE FROM {table} WHERE {col} NOT LIKE 'SRV-%'")
            dropped = cur.rowcount
            total_renamed += renamed
            total_dropped += dropped
            print(
                f"  {table}.{col}: {bare} bare -> {renamed} renombradas, "
                f"{dropped} duplicadas descartadas"
            )

        if dry_run:
            print("\n[dry-run] No se realizaron cambios.")
            return

        conn.commit()
        print(
            f"\n[OK] Consolidacion completada: {total_renamed} renombradas a SRV-, "
            f"{total_dropped} duplicadas descartadas"
        )
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Normaliza suministro_ids a formato SRV-xxx")
    parser.add_argument(
        "--db",
        default="data/plataforma_clientes.db",
        help="Ruta al archivo SQLite (default: data/plataforma_clientes.db)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Solo reporta, no modifica")
    args = parser.parse_args()

    db_path = args.db
    if not Path(db_path).exists():
        print(f"Error: base de datos no encontrada en '{db_path}'")
        sys.exit(1)

    print(f"Migrando {db_path}{'  [DRY RUN]' if args.dry_run else ''}...")
    _migrate(db_path, args.dry_run)


if __name__ == "__main__":
    main()
