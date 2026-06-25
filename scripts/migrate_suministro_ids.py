"""Migración one-shot: normaliza suministro_ids bare ('2817670') a canónico ('SRV-2817670').

El bulk reader de Oracle almacenaba SRV_CODIGO sin prefijo. Este script corrige los
registros existentes en consumo_diario, consumo_horario y suministros antes del deploy
del fix de normalización.

Uso:
    DATABASE_URL=sqlite:///epec.db uv run scripts/migrate_suministro_ids.py [--dry-run]
"""

import argparse
import sqlite3
import sys
from pathlib import Path

_TABLES: list[tuple[str, str]] = [
    ("consumo_diario", "suministro_id"),
    ("consumo_horario", "suministro_id"),
    ("suministros", "srv_codigo"),
    ("proyeccion_mensual", "suministro_id"),
    ("objetivo_consumo", "suministro_id"),
    ("notificaciones_config", "suministro_id"),
]


def _migrate(db_path: str, dry_run: bool) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        total_updated = 0
        for table, col in _TABLES:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cur.fetchone():
                print(f"  [skip] tabla '{table}' no existe")
                continue

            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} NOT LIKE 'SRV-%'")
            (count,) = cur.fetchone()
            print(f"  {table}.{col}: {count} filas sin prefijo")

            if count > 0 and not dry_run:
                cur.execute(
                    f"UPDATE {table} SET {col} = 'SRV-' || {col} WHERE {col} NOT LIKE 'SRV-%'"
                )
                total_updated += count

        # vecinos_cache: limpiar cache para que se regenere con IDs corregidos en el próximo login
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vecinos_cache'")
        if cur.fetchone():
            cur.execute("SELECT COUNT(*) FROM vecinos_cache")
            (vc_count,) = cur.fetchone()
            print(f"  vecinos_cache: {vc_count} entradas — se borrarán para regeneración")
            if not dry_run:
                cur.execute("DELETE FROM vecinos_cache")

        if not dry_run:
            conn.commit()
            print(f"\n✓ Migración completada: {total_updated} filas actualizadas, cache limpiada")
        else:
            print(
                f"\n[dry-run] No se realizaron cambios. {total_updated} filas serían actualizadas"
            )
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Normaliza suministro_ids a formato SRV-xxx")
    parser.add_argument("--db", default="epec.db", help="Ruta al archivo SQLite (default: epec.db)")
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
