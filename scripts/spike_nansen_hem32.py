"""Spike: bloque K — exploración tablas NANSEN HEM32 y BKP_LCT_NANSEN.

Encontradas en J12. Candidatas a contener perfiles 15-min NANSEN.
NO modifica nada. Solo SELECT.

Uso:
    uv run python scripts/spike_nansen_hem32.py
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

import oracledb

_REQUIRED = ("OR_HOST", "OR_USER", "OR_PASS", "OR_SERVICE_NAME")
SEP = "-" * 72

# Medidor NANSEN de prueba (desde GEOREF.VM_INTELIGENTES suministro=2817670)
# En SIGEC: med_codigo='91013486', en GEOREF.VM_INTELIGENTES: medidor='91013486'
# Medidores NANSEN reales (formato 71XXXXXX, de I4):
_NANSEN_71_EJEMPLO = "71100824"
_NANSEN_71_SUMINISTRO = "488136"
# Medidor del suministro de prueba original
_MED_SIGEC = "91013486"
_SUMINISTRO_PRUEBA = "2817670"


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
    print("  SPIKE K — Tablas NANSEN HEM32: XXASCENTIO, XXMD, GEOREF BKP")
    print(f"{'=' * 72}\n")

    conn = _conectar()
    try:
        with conn.cursor() as cur:
            # ─── K1: XXASCENTIO.XXMD_LECTURAS_HEM32 — estructura ─────────────
            run(
                cur,
                "K1 — Columnas de XXASCENTIO.XXMD_LECTURAS_HEM32",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'XXASCENTIO' AND table_name = 'XXMD_LECTURAS_HEM32'
                ORDER BY column_id
                """,
                limit=50,
            )

            # ─── K2: XXASCENTIO.XXMD_LECTURAS_HEM32 — muestra libre ─────────
            run(
                cur,
                "K2 — XXASCENTIO.XXMD_LECTURAS_HEM32 muestra libre (5 filas)",
                """
                SELECT *
                FROM XXASCENTIO.XXMD_LECTURAS_HEM32
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── K3: XXASCENTIO.XXMD_LECTURAS_HEM32_HS — estructura ──────────
            run(
                cur,
                "K3 — Columnas de XXASCENTIO.XXMD_LECTURAS_HEM32_HS",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'XXASCENTIO' AND table_name = 'XXMD_LECTURAS_HEM32_HS'
                ORDER BY column_id
                """,
                limit=50,
            )

            # ─── K4: XXASCENTIO.XXMD_LECTURAS_HEM32_HS — muestra libre ──────
            run(
                cur,
                "K4 — XXASCENTIO.XXMD_LECTURAS_HEM32_HS muestra libre (5 filas)",
                """
                SELECT *
                FROM XXASCENTIO.XXMD_LECTURAS_HEM32_HS
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── K5: XXMD.XXMD_LECTURAS — estructura ──────────────────────────
            run(
                cur,
                "K5 — Columnas de XXMD.XXMD_LECTURAS",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'XXMD' AND table_name = 'XXMD_LECTURAS'
                ORDER BY column_id
                """,
                limit=50,
            )

            # ─── K6: XXMD.XXMD_LECTURAS — muestra libre ───────────────────────
            run(
                cur,
                "K6 — XXMD.XXMD_LECTURAS muestra libre (5 filas)",
                """
                SELECT *
                FROM XXMD.XXMD_LECTURAS
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── K7: XXSAMPLAT.XXMD_LECTURAS_SAMPLAT — estructura ─────────────
            run(
                cur,
                "K7 — Columnas de XXSAMPLAT.XXMD_LECTURAS_SAMPLAT",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'XXSAMPLAT' AND table_name = 'XXMD_LECTURAS_SAMPLAT'
                ORDER BY column_id
                """,
                limit=50,
            )

            # ─── K8: XXSAMPLAT.XXMD_LECTURAS_SAMPLAT — muestra libre ─────────
            run(
                cur,
                "K8 — XXSAMPLAT.XXMD_LECTURAS_SAMPLAT muestra libre (5 filas)",
                """
                SELECT *
                FROM XXSAMPLAT.XXMD_LECTURAS_SAMPLAT
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── K9: GEOREF.BKP_LCT_NANSEN_GC — estructura ───────────────────
            run(
                cur,
                "K9 — Columnas de GEOREF.BKP_LCT_NANSEN_GC_2023_10_23",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'GEOREF' AND table_name = 'BKP_LCT_NANSEN_GC_2023_10_23'
                ORDER BY column_id
                """,
                limit=50,
            )

            # ─── K10: GEOREF.BKP_LCT_NANSEN_GC — muestra libre ───────────────
            run(
                cur,
                "K10 — GEOREF.BKP_LCT_NANSEN_GC_2023_10_23 muestra libre (5 filas)",
                """
                SELECT *
                FROM GEOREF.BKP_LCT_NANSEN_GC_2023_10_23
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── K11: GEOREF.DATA_MD_PROFILE_MINUTELY_SH1 — estructura ───────
            run(
                cur,
                "K11 — Columnas de GEOREF.DATA_MD_PROFILE_MINUTELY_SH1",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'GEOREF' AND table_name = 'DATA_MD_PROFILE_MINUTELY_SH1'
                ORDER BY column_id
                """,
                limit=50,
            )

            # ─── K12: GEOREF.DATA_MD_PROFILE_MINUTELY_SH1 — muestra libre ────
            run(
                cur,
                "K12 — GEOREF.DATA_MD_PROFILE_MINUTELY_SH1 muestra libre (5 filas)",
                """
                SELECT *
                FROM GEOREF.DATA_MD_PROFILE_MINUTELY_SH1
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── K13: XXASCENTIO — todos los objetos accesibles ───────────────
            run(
                cur,
                "K13 — Todos los objetos TABLE/VIEW en XXASCENTIO",
                """
                SELECT owner, object_name, object_type
                FROM all_objects
                WHERE owner = 'XXASCENTIO'
                  AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
                ORDER BY object_type, object_name
                """,
                limit=30,
            )

            # ─── K14: XXSAMPLAT — todos los objetos accesibles ────────────────
            run(
                cur,
                "K14 — Todos los objetos TABLE/VIEW en XXSAMPLAT",
                """
                SELECT owner, object_name, object_type
                FROM all_objects
                WHERE owner = 'XXSAMPLAT'
                  AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
                ORDER BY object_type, object_name
                """,
                limit=30,
            )

            # ─── K15: Buscar nuestro medidor NANSEN 91013486 en HEM32 ─────────
            # (intentar varios formatos)
            run(
                cur,
                f"K15 — HEM32: buscar medidor '{_MED_SIGEC}' (variantes de formato)",
                """
                SELECT *
                FROM XXASCENTIO.XXMD_LECTURAS_HEM32
                WHERE ROWNUM <= 5
                  AND (TO_CHAR(MED_CODIGO) LIKE '%91013486%'
                    OR TO_CHAR(MED_CODIGO) LIKE '%91013486%')
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── K16: Buscar medidor NANSEN 71XXXXXX en HEM32 ────────────────
            run(
                cur,
                f"K16 — HEM32: buscar medidor NANSEN '{_NANSEN_71_EJEMPLO}' (suministro {_NANSEN_71_SUMINISTRO})",
                """
                SELECT *
                FROM XXASCENTIO.XXMD_LECTURAS_HEM32
                WHERE TO_CHAR(MED_CODIGO) LIKE '%71100824%'
                   OR TO_CHAR(MED_CODIGO) = '71100824'
                FETCH FIRST 10 ROWS ONLY
                """,
                limit=10,
            )

            # ─── K17: XXSIGEC.XXCO_ULTIMA_TELEMEDICION_VM — estructura ────────
            run(
                cur,
                "K17 — Columnas de XXSIGEC.XXCO_ULTIMA_TELEMEDICION_VM",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'XXSIGEC' AND table_name = 'XXCO_ULTIMA_TELEMEDICION_VM'
                ORDER BY column_id
                """,
                limit=30,
            )

            # ─── K18: XXSIGEC.XXCO_ULTIMA_TELEMEDICION_VM — muestra libre ─────
            run(
                cur,
                "K18 — XXSIGEC.XXCO_ULTIMA_TELEMEDICION_VM muestra libre (5 filas)",
                """
                SELECT *
                FROM XXSIGEC.XXCO_ULTIMA_TELEMEDICION_VM
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── K19: XXSIGEC.TELEMEDIDOS — estructura ────────────────────────
            run(
                cur,
                "K19 — Columnas de XXSIGEC.TELEMEDIDOS",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'XXSIGEC' AND table_name = 'TELEMEDIDOS'
                ORDER BY column_id
                """,
                limit=30,
            )

            # ─── K20: XXSIGEC.TELEMEDIDOS — muestra libre ─────────────────────
            run(
                cur,
                "K20 — XXSIGEC.TELEMEDIDOS muestra libre (5 filas)",
                """
                SELECT *
                FROM XXSIGEC.TELEMEDIDOS
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── K21: XXMD.XXMD_LECTURAS — buscar nuestro medidor ─────────────
            run(
                cur,
                f"K21 — XXMD.XXMD_LECTURAS: buscar '{_MED_SIGEC}' y '{_NANSEN_71_EJEMPLO}'",
                """
                SELECT *
                FROM XXMD.XXMD_LECTURAS
                WHERE TO_CHAR(MED_CODIGO) IN ('91013486', '71100824', '71100876')
                   OR TO_CHAR(MED_NRO_EQUIPO) IN ('91013486', '71100824', '71100876')
                FETCH FIRST 10 ROWS ONLY
                """,
                limit=10,
            )

            # ─── K22: XXASCENTIO.XXMD_LECTURAS_GC — estructura ────────────────
            run(
                cur,
                "K22 — Columnas de XXASCENTIO.XXMD_LECTURAS_GC (grandes clientes)",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'XXASCENTIO' AND table_name = 'XXMD_LECTURAS_GC'
                ORDER BY column_id
                """,
                limit=30,
            )

    finally:
        conn.rollback()
        conn.close()

    print("=" * 72)
    print("  SPIKE K — NANSEN HEM32 COMPLETADO")
    print("=" * 72)


if __name__ == "__main__":
    main()
