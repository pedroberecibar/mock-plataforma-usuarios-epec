"""Spike M — Datos de cliente para medidores CLOU del listado.

Consulta VM_INTELIGENTES para obtener: suministro, nombre (razón social),
documento, cuit, domicilio, coordenadas, tarifa para medidores CLOU reales.
También explora tablas de clientes en XXSIGEC.

Uso:
    uv run python -u scripts/spike_cliente_oracle.py
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
sys.stdout.reconfigure(line_buffering=True)

import oracledb

_REQUIRED = ("OR_HOST", "OR_USER", "OR_PASS", "OR_SERVICE_NAME")
SEP = "-" * 72

# Muestra de medidores CLOU del listado (mix de prefijos)
MUESTRA_CLOU = [
    "90008989",
    "90008245",
    "90008983",  # 90008XXX
    "90010533",
    "90010534",
    "90010535",  # 90010XXX
    "70096469",
    "70096451",
    "70096527",  # 70XXXXXX
    "70085039",
    "70084821",
]


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


def run(cur: oracledb.Cursor, titulo: str, sql: str, params=None, limit: int = 20) -> list:
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
    print("  SPIKE M — Datos de cliente para medidores CLOU del listado")
    print(f"{'=' * 72}\n")

    conn = _conectar()
    print("  Conectado OK\n")

    try:
        with conn.cursor() as cur:
            # M1: Columnas disponibles en VM_INTELIGENTES (buscar campos de cliente)
            run(
                cur,
                "M1 — Columnas de VM_INTELIGENTES con 'razon', 'nombre', 'cuit', 'doc', 'dom', 'tarif'",
                """
                SELECT column_name, data_type, data_length
                FROM all_tab_columns
                WHERE owner = 'GEOREF' AND table_name = 'VM_INTELIGENTES'
                  AND (
                      UPPER(column_name) LIKE '%RAZON%'
                      OR UPPER(column_name) LIKE '%NOMBRE%'
                      OR UPPER(column_name) LIKE '%CUIT%'
                      OR UPPER(column_name) LIKE '%DOMIC%'
                      OR UPPER(column_name) LIKE '%DOCUM%'
                      OR UPPER(column_name) LIKE '%DNI%'
                      OR UPPER(column_name) LIKE '%TARIF%'
                      OR UPPER(column_name) LIKE '%LATIT%'
                      OR UPPER(column_name) LIKE '%LONGIT%'
                      OR UPPER(column_name) LIKE '%TELEF%'
                      OR UPPER(column_name) LIKE '%EMAIL%'
                      OR UPPER(column_name) LIKE '%MAIL%'
                      OR UPPER(column_name) LIKE '%CALLE%'
                      OR UPPER(column_name) LIKE '%LOCAL%'
                      OR UPPER(column_name) LIKE '%BARRI%'
                      OR UPPER(column_name) LIKE '%SUMIN%'
                      OR UPPER(column_name) LIKE '%MEDID%'
                  )
                ORDER BY column_id
                """,
                limit=60,
            )

            # M2: Datos reales para muestra CLOU del listado
            ph = ", ".join(f":m{i}" for i in range(len(MUESTRA_CLOU)))
            params_m2 = {f"m{i}": v for i, v in enumerate(MUESTRA_CLOU)}
            run(
                cur,
                f"M2 — VM_INTELIGENTES: datos completos para {len(MUESTRA_CLOU)} medidores CLOU",
                f"""
                SELECT *
                FROM GEOREF.VM_INTELIGENTES
                WHERE medidor IN ({ph})
                """,
                params_m2,
                limit=15,
            )

            # M3: Buscar tabla de clientes en XXSIGEC
            run(
                cur,
                "M3 — Tablas XXSIGEC con CLIENTE, TITULAR, SOCIO en el nombre",
                """
                SELECT object_name, object_type
                FROM all_objects
                WHERE owner = 'XXSIGEC'
                  AND (UPPER(object_name) LIKE '%CLIENTE%'
                    OR UPPER(object_name) LIKE '%TITULAR%'
                    OR UPPER(object_name) LIKE '%SOCIO%'
                    OR UPPER(object_name) LIKE '%USUARIO%'
                    OR UPPER(object_name) LIKE '%PERSON%'
                    OR UPPER(object_name) LIKE '%CUENTA%')
                  AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
                ORDER BY object_type, object_name
                """,
                limit=30,
            )

            # M4: Suministros asociados a medidores del listado en XXSIGEC
            run(
                cur,
                "M4 — XXSIGEC.XXCO_EQUIPOS: medidor → suministro (estructura)",
                """
                SELECT column_name, data_type, data_length
                FROM all_tab_columns
                WHERE owner = 'XXSIGEC' AND table_name = 'XXCO_EQUIPOS'
                ORDER BY column_id
                """,
                limit=30,
            )

            # M5: Buscar en XXCO_EQUIPOS para obtener SRV_CODIGO de nuestros medidores
            run(
                cur,
                f"M5 — XXCO_EQUIPOS: medidores del listado → suministro",
                f"""
                SELECT *
                FROM XXSIGEC.XXCO_EQUIPOS
                WHERE MED_CODIGO IN ({ph})
                FETCH FIRST 12 ROWS ONLY
                """,
                params_m2,
                limit=12,
            )

            # M6: Columnas de XXCO_SUMINISTROS (si existe)
            run(
                cur,
                "M6 — Columnas de XXSIGEC.XXCO_SUMINISTROS",
                """
                SELECT column_name, data_type, data_length
                FROM all_tab_columns
                WHERE owner = 'XXSIGEC' AND table_name = 'XXCO_SUMINISTROS'
                ORDER BY column_id
                """,
                limit=50,
            )

            # M7: XXCO_SUMINISTROS muestra libre para suministro conocido (de I5 anterior)
            run(
                cur,
                "M7 — XXCO_SUMINISTROS: muestra libre",
                """
                SELECT *
                FROM XXSIGEC.XXCO_SUMINISTROS
                FETCH FIRST 3 ROWS ONLY
                """,
                limit=3,
            )

    finally:
        conn.rollback()
        conn.close()

    print("=" * 72)
    print("  SPIKE M COMPLETADO")
    print("=" * 72)


if __name__ == "__main__":
    main()
