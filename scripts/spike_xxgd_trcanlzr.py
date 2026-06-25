"""Spike L — XXGD + TRCANLZR: solo consultas a catálogo (ALL_*).

Sin SELECT * de tablas de datos para evitar cuelgues.
Versión segura: solo ALL_OBJECTS, ALL_TAB_COLUMNS, ALL_TABLES.

Uso:
    uv run python -u scripts/spike_xxgd_trcanlzr.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_root = Path(__file__).parent.parent
_env_path = _root / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

sys.path.insert(0, str(_root / "src"))
sys.stdout.reconfigure(line_buffering=True)  # flush cada línea

import oracledb

_REQUIRED = ("OR_HOST", "OR_USER", "OR_PASS", "OR_SERVICE_NAME")
SEP = "-" * 72

_MED_SIGEC = "91013486"
_MED_NANSEN_71 = "71100824"


def _conectar() -> oracledb.Connection:
    missing = [v for v in _REQUIRED if not os.environ.get(v)]
    if missing:
        print(f"[spike] Faltan variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    instant_client = os.environ.get("OR_INSTANT_CLIENT", "")
    if instant_client and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(instant_client)
    if instant_client:
        try:
            oracledb.init_oracle_client(lib_dir=instant_client)
        except oracledb.ProgrammingError as exc:
            if "already" not in str(exc).lower():
                raise

    dsn = oracledb.makedsn(
        host=os.environ["OR_HOST"],
        port=int(os.environ.get("OR_PORT", "1521")),
        service_name=os.environ["OR_SERVICE_NAME"],
    )
    conn = oracledb.connect(
        user=os.environ["OR_USER"],
        password=os.environ["OR_PASS"],
        dsn=dsn,
    )
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
    return conn


def run(
    cur: oracledb.Cursor, titulo: str, sql: str, params: dict | None = None, limit: int = 20
) -> list:
    print(SEP)
    print(f"  {titulo}")
    print(SEP)
    try:
        cur.execute(sql, params or {})
        cols = [d[0].lower() for d in cur.description]
        rows = cur.fetchmany(limit)
        print(f"  cols: {cols}")
        print(f"  filas ({len(rows)}):")
        for row in rows:
            print(f"    {dict(zip(cols, row, strict=False))}")
        if not rows:
            print("    (sin resultados)")
        print()
        return rows
    except Exception as exc:
        print(f"  ERROR: {exc}\n")
        return []


def main() -> None:
    print(f"\n{'=' * 72}")
    print("  SPIKE L — XXGD + TRCANLZR (solo catálogo — sin SELECT de datos)")
    print(f"{'=' * 72}\n")

    conn = _conectar()
    print("  Conectado OK\n")

    try:
        with conn.cursor() as cur:
            # ─── XXGD ─────────────────────────────────────────────────────

            # L1: Todos los objetos XXGD
            run(
                cur,
                "L1 — Todos los objetos TABLE/VIEW en XXGD",
                """
                SELECT object_name, object_type
                FROM all_objects
                WHERE owner = 'XXGD'
                  AND object_type IN ('TABLE','VIEW','SYNONYM')
                ORDER BY object_type, object_name
                """,
                limit=60,
            )

            # L2: Tablas XXGD con num_rows (estadísticas)
            run(
                cur,
                "L2 — XXGD tablas con num_rows estimado",
                """
                SELECT table_name, num_rows, last_analyzed
                FROM all_tables
                WHERE owner = 'XXGD'
                ORDER BY num_rows DESC NULLS LAST
                """,
                limit=60,
            )

            # L3: Todas las columnas de todas las tablas XXGD
            run(
                cur,
                "L3 — Todas las columnas de tablas XXGD",
                """
                SELECT table_name, column_name, data_type, data_length
                FROM all_tab_columns
                WHERE owner = 'XXGD'
                ORDER BY table_name, column_id
                """,
                limit=250,
            )

            # ─── TRCANLZR ─────────────────────────────────────────────────

            print(f"\n{'=' * 72}")
            print("  TRCANLZR")
            print(f"{'=' * 72}\n")

            # L4: Todos los objetos TRCANLZR
            run(
                cur,
                "L4 — Todos los objetos TABLE/VIEW en TRCANLZR",
                """
                SELECT object_name, object_type
                FROM all_objects
                WHERE owner = 'TRCANLZR'
                  AND object_type IN ('TABLE','VIEW','SYNONYM')
                ORDER BY object_type, object_name
                """,
                limit=40,
            )

            # L5: Tablas TRCANLZR con num_rows
            run(
                cur,
                "L5 — TRCANLZR tablas con num_rows estimado",
                """
                SELECT table_name, num_rows, last_analyzed
                FROM all_tables
                WHERE owner = 'TRCANLZR'
                ORDER BY num_rows DESC NULLS LAST
                """,
                limit=30,
            )

            # L6: Todas las columnas de tablas TRCANLZR
            run(
                cur,
                "L6 — Todas las columnas de tablas TRCANLZR",
                """
                SELECT table_name, column_name, data_type, data_length
                FROM all_tab_columns
                WHERE owner = 'TRCANLZR'
                ORDER BY table_name, column_id
                """,
                limit=300,
            )

            # ─── XXSAMPLAT extra (desde K) ────────────────────────────────

            print(f"\n{'=' * 72}")
            print("  XXSAMPLAT extra")
            print(f"{'=' * 72}\n")

            # L7: CDR_UNIDADs y granularidad de XXSAMPLAT.XXMD_LECTURAS_SAMPLAT
            run(
                cur,
                "L7 — XXSAMPLAT.XXMD_LECTURAS_SAMPLAT: CDR_UNIDAD y rango de fechas",
                """
                SELECT CDR_UNIDAD,
                       COUNT(*) AS n,
                       MIN(FECHA_LECTURA) AS desde,
                       MAX(FECHA_LECTURA) AS hasta
                FROM XXSAMPLAT.XXMD_LECTURAS_SAMPLAT
                GROUP BY CDR_UNIDAD
                ORDER BY n DESC
                """,
                limit=20,
            )

            # L8: Granularidad — ¿hay filas con hora != 00:00?
            run(
                cur,
                "L8 — XXSAMPLAT.XXMD_LECTURAS_SAMPLAT: ¿filas sub-diarias?",
                """
                SELECT
                  COUNT(*) AS total,
                  SUM(CASE WHEN TO_CHAR(FECHA_LECTURA,'HH24:MI:SS') != '00:00:00'
                           THEN 1 ELSE 0 END) AS con_hora,
                  MIN(FECHA_LECTURA) AS desde,
                  MAX(FECHA_LECTURA) AS hasta
                FROM XXSAMPLAT.XXMD_LECTURAS_SAMPLAT
                """,
                limit=5,
            )

            # L9: Rangos de med_codigo en SAMPLAT
            run(
                cur,
                "L9 — XXSAMPLAT.XXMD_LECTURAS_SAMPLAT: rangos de med_codigo",
                """
                SELECT
                  TRUNC(MED_CODIGO / 1000000) * 1000000 AS prefijo,
                  COUNT(DISTINCT MED_CODIGO) AS n_medidores,
                  MIN(MED_CODIGO) AS min_med,
                  MAX(MED_CODIGO) AS max_med
                FROM XXSAMPLAT.XXMD_LECTURAS_SAMPLAT
                GROUP BY TRUNC(MED_CODIGO / 1000000) * 1000000
                ORDER BY prefijo
                """,
                limit=20,
            )

            # L10: Buscar medidor prueba en SAMPLAT
            run(
                cur,
                f"L10 — XXSAMPLAT: buscar '{_MED_SIGEC}' y '{_MED_NANSEN_71}'",
                """
                SELECT *
                FROM XXSAMPLAT.XXMD_LECTURAS_SAMPLAT
                WHERE MED_CODIGO IN (91013486, 71100824, 71100876)
                ORDER BY FECHA_LECTURA DESC
                FETCH FIRST 20 ROWS ONLY
                """,
                limit=20,
            )

            # L11: XXSAMPLAT.XXMD_METER_MANAGEMENT — estructura + muestra
            run(
                cur,
                "L11 — XXSAMPLAT.XXMD_METER_MANAGEMENT: columnas",
                """
                SELECT column_name, data_type, data_length
                FROM all_tab_columns
                WHERE owner = 'XXSAMPLAT' AND table_name = 'XXMD_METER_MANAGEMENT'
                ORDER BY column_id
                """,
                limit=30,
            )

    finally:
        conn.rollback()
        conn.close()

    print("=" * 72)
    print("  SPIKE L COMPLETADO")
    print("=" * 72)


if __name__ == "__main__":
    main()
