"""Paso 0: verifica schema y datos de GEOREF.VM_INTELIGENTES para el cambio vecinos-por-subestacion.

NO MODIFICA NADA. Solo SELECT.

Uso:
    uv run python scripts/spike_verify_vm_inteligentes.py
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

import oracledb  # noqa: E402

SEP = "=" * 72


def _conectar() -> oracledb.Connection:
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
    conn = oracledb.connect(user=os.environ["OR_USER"], password=os.environ["OR_PASS"], dsn=dsn)
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
    return conn


def run(
    cur: oracledb.Cursor, titulo: str, sql: str, params: dict | None = None, limit: int = 10
) -> list:
    print(f"\n{SEP}")
    print(f"  {titulo}")
    print(SEP)
    try:
        cur.execute(sql, params or {})
        cols = [d[0] for d in cur.description]
        rows = cur.fetchmany(limit)
        print(f"  cols: {cols}")
        print(f"  filas ({len(rows)}):")
        for row in rows:
            print(f"    {dict(zip(cols, row, strict=False))}")
        if not rows:
            print("    (sin resultados)")
        return rows
    except Exception as exc:
        print(f"  ERROR: {exc}")
        return []


def main() -> None:
    print("Conectando a Oracle...")
    conn = _conectar()
    print("OK\n")

    with conn.cursor() as cur:
        # V1: Columnas exactas de VM_INTELIGENTES
        run(
            cur,
            "V1 — Columnas de GEOREF.VM_INTELIGENTES (nombres, tipos)",
            """
            SELECT column_name, data_type, data_length, nullable
            FROM all_tab_columns
            WHERE owner = 'GEOREF' AND table_name = 'VM_INTELIGENTES'
            ORDER BY column_id
        """,
            limit=50,
        )

        # V2: Muestra de 3 filas completas para ver datos reales
        run(
            cur,
            "V2 — SELECT * FROM GEOREF.VM_INTELIGENTES (3 filas)",
            """
            SELECT * FROM GEOREF.VM_INTELIGENTES FETCH FIRST 3 ROWS ONLY
        """,
            limit=3,
        )

        # V3: Confirmar columna SUBESTACION existe y tiene datos
        run(
            cur,
            "V3 — COUNT y NULLs en columna SUBESTACION",
            """
            SELECT
                COUNT(*) AS total,
                COUNT(SUBESTACION) AS con_subestacion,
                COUNT(*) - COUNT(SUBESTACION) AS sin_subestacion
            FROM GEOREF.VM_INTELIGENTES
        """,
        )

        # V4: Valores distintos de SUBESTACION (muestra)
        run(
            cur,
            "V4 — DISTINCT SUBESTACION (primeros 10)",
            """
            SELECT DISTINCT SUBESTACION, COUNT(*) AS n_suministros
            FROM GEOREF.VM_INTELIGENTES
            WHERE SUBESTACION IS NOT NULL
            GROUP BY SUBESTACION
            ORDER BY n_suministros DESC
            FETCH FIRST 10 ROWS ONLY
        """,
            limit=10,
        )

        # V5: Verificar columna SUMINISTRO (join key con XXSIGEC.SERVICIOS.SRV_CODIGO)
        # Tomar 5 suministros de VM_INTELIGENTES y verificar que existen en XXSIGEC.SERVICIOS
        run(
            cur,
            "V5 — Cross-check: SUMINISTRO de VM_INTELIGENTES vs SRV_CODIGO de XXSIGEC.SERVICIOS (5 filas)",
            """
            SELECT v.SUMINISTRO, s.SRV_CODIGO, s.SRV_GPS_LATITUD, s.SRV_GPS_LONGITUD
            FROM GEOREF.VM_INTELIGENTES v
            JOIN XXSIGEC.SERVICIOS s ON s.SRV_CODIGO = v.SUMINISTRO
            FETCH FIRST 5 ROWS ONLY
        """,
            limit=5,
        )

        # V6: Query de subestacion para un suministro conocido del seed_demo
        # Usar el primer suministro de la muestra real
        run(
            cur,
            "V6 — Subestacion del suministro 2817670 (Nansen de prueba)",
            """
            SELECT SUMINISTRO, SUBESTACION
            FROM GEOREF.VM_INTELIGENTES
            WHERE SUMINISTRO = '2817670'
        """,
        )

        # V7: Vecinos por subestacion (la query candidata real)
        run(
            cur,
            "V7 — Vecinos de 2817670 via subestacion (query candidata)",
            """
            SELECT SUMINISTRO
            FROM   GEOREF.VM_INTELIGENTES
            WHERE  SUBESTACION = (
                       SELECT SUBESTACION
                       FROM   GEOREF.VM_INTELIGENTES
                       WHERE  SUMINISTRO = '2817670'
                       FETCH FIRST 1 ROW ONLY
                   )
              AND  SUMINISTRO != '2817670'
            FETCH FIRST 20 ROWS ONLY
        """,
            limit=20,
        )

        # V8: Cuantos vecinos totales trae la subestacion
        run(
            cur,
            "V8 — Total vecinos de 2817670 via subestacion",
            """
            SELECT COUNT(*) AS n_vecinos
            FROM   GEOREF.VM_INTELIGENTES
            WHERE  SUBESTACION = (
                       SELECT SUBESTACION
                       FROM   GEOREF.VM_INTELIGENTES
                       WHERE  SUMINISTRO = '2817670'
                       FETCH FIRST 1 ROW ONLY
                   )
              AND  SUMINISTRO != '2817670'
        """,
        )

        # V9: Ver columna de medidor en VM_INTELIGENTES (para optimizar scheduler)
        # Buscar columnas con 'MED', 'EQUIP', 'METER', 'DEVICE'
        run(
            cur,
            "V9 — Columnas de VM_INTELIGENTES que contienen MED/EQUIP/METER/DEVICE",
            """
            SELECT column_name, data_type
            FROM all_tab_columns
            WHERE owner = 'GEOREF' AND table_name = 'VM_INTELIGENTES'
              AND (
                  UPPER(column_name) LIKE '%MED%'
                  OR UPPER(column_name) LIKE '%EQUIP%'
                  OR UPPER(column_name) LIKE '%METER%'
                  OR UPPER(column_name) LIKE '%DEVICE%'
              )
            ORDER BY column_id
        """,
            limit=20,
        )

    conn.rollback()
    conn.close()
    print(f"\n{SEP}")
    print("  Verificación completa.")
    print(SEP)


if __name__ == "__main__":
    main()
