"""Spike: bloques I y J — listado mi-activos + búsqueda tabla NANSEN.

Solo corre las queries nuevas. NO modifica nada.

Uso:
    uv run python scripts/spike_listado_nansen.py
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
    print("  SPIKE — BLOQUE I: TELEMEDIBLE + listado medidores + QUERY_ASSET_METER")
    print(f"{'=' * 72}\n")

    conn = _conectar()
    try:
        with conn.cursor() as cur:
            # ─── BLOQUE I ────────────────────────────────────────────────────

            # I1: DISTINCT TELEMEDIBLE (pedido explícito del usuario)
            run(
                cur,
                "I1 — SELECT DISTINCT TELEMEDIBLE, COUNT(*) FROM GEOREF.VM_INTELIGENTES",
                """
                SELECT TELEMEDIBLE, COUNT(*) AS n
                FROM GEOREF.VM_INTELIGENTES
                WHERE TELEMEDIBLE IS NOT NULL
                GROUP BY TELEMEDIBLE
                ORDER BY n DESC
                """,
                limit=20,
            )

            # I2: VM_INTELIGENTES — columnas completas (lista de nombres + tipos)
            run(
                cur,
                "I2 — Columnas de GEOREF.VM_INTELIGENTES (todos los campos)",
                """
                SELECT column_name, data_type, data_length, nullable
                FROM all_tab_columns
                WHERE owner = 'GEOREF' AND table_name = 'VM_INTELIGENTES'
                ORDER BY column_id
                """,
                limit=150,
            )

            # I3: SELECT * muestra real (3 filas) para ver valores reales
            run(
                cur,
                "I3 — SELECT * FROM GEOREF.VM_INTELIGENTES FETCH FIRST 3 ROWS ONLY",
                """
                SELECT *
                FROM GEOREF.VM_INTELIGENTES
                FETCH FIRST 3 ROWS ONLY
                """,
                limit=3,
            )

            # I4: Medidores NANSEN en VM_INTELIGENTES (suministro, medidor, pct, origen)
            run(
                cur,
                "I4 — VM_INTELIGENTES: medidores NANSEN (5 filas — ver formato de medidor)",
                """
                SELECT suministro, medidor, telemedible, pct, origen_lectura,
                       dc_latitud, dc_longitud
                FROM GEOREF.VM_INTELIGENTES
                WHERE UPPER(telemedible) = 'NANSEN'
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # I5: Medidores CLOU en VM_INTELIGENTES
            run(
                cur,
                "I5 — VM_INTELIGENTES: medidores CLOU (5 filas — ver formato de medidor)",
                """
                SELECT suministro, medidor, telemedible, pct, origen_lectura,
                       dc_latitud, dc_longitud
                FROM GEOREF.VM_INTELIGENTES
                WHERE UPPER(telemedible) = 'CLOU'
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # I6: Medidores 70XXXXXX del listado en QUERY_ASSET_METER (zero-padded a 12 chars)
            muestra_70 = [
                "70096469",
                "70096451",
                "70096527",
                "70096463",
                "70096530",
                "70085039",
                "70084821",
                "70099630",
                "70085042",
                "70084822",
            ]
            sn_padded = [f"000{m}" for m in muestra_70]
            ph = ", ".join(f":sn{i}" for i in range(len(sn_padded)))
            params_i6 = {f"sn{i}": sn for i, sn in enumerate(sn_padded)}
            run(
                cur,
                f"I6 — QUERY_ASSET_METER: {len(muestra_70)} medidores 70XXXXXX del listado (zero-padded)",
                f"SELECT ID, SN, NAME, MAC FROM GEOREF.QUERY_ASSET_METER WHERE SN IN ({ph})",
                params_i6,
                limit=15,
            )

            # I7: Medidores 90008XXX del listado en QUERY_ASSET_METER
            muestra_90008 = ["90008989", "90008245", "90008983", "90008578", "90008384"]
            sn_padded_90 = [f"000{m}" for m in muestra_90008]
            ph_90 = ", ".join(f":sn{i}" for i in range(len(sn_padded_90)))
            params_i7 = {f"sn{i}": sn for i, sn in enumerate(sn_padded_90)}
            run(
                cur,
                f"I7 — QUERY_ASSET_METER: {len(muestra_90008)} medidores 90008XXX del listado",
                f"SELECT ID, SN, NAME, MAC FROM GEOREF.QUERY_ASSET_METER WHERE SN IN ({ph_90})",
                params_i7,
                limit=10,
            )

            # I8: Confirmar SHENYU1 data para un 70XXXXXX del listado (si I6 tiene resultados)
            run(
                cur,
                "I8 — SHENYU1 filas recientes (últimos 7 días) para 70XXXXXX del listado",
                """
                SELECT q.SN, COUNT(*) AS n_filas, MAX(s.TV) AS ultima_lectura,
                       MIN(s.TV) AS primera_lectura
                FROM GEOREF.QUERY_ASSET_METER q
                JOIN GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 s
                  ON s.DEVICE_ID = q.ID
                WHERE q.SN IN (
                    '000070096469','000070096451','000070096527',
                    '000070085039','000070084821','000070099630',
                    '000070096463','000070096530','000070085042'
                )
                  AND s.TV >= SYSDATE - 7
                GROUP BY q.SN
                ORDER BY n_filas DESC
                FETCH FIRST 5 ROWS ONLY
                """,
                limit=5,
            )

            # ─── BLOQUE J ────────────────────────────────────────────────────
            print(f"\n{'=' * 72}")
            print("  SPIKE — BLOQUE J: Buscando tabla de perfiles NANSEN")
            print(f"{'=' * 72}\n")

            # J1: ALL_OBJECTS con MDM en el nombre
            run(
                cur,
                "J1 — ALL_OBJECTS con 'MDM' en el nombre (TABLE/VIEW/SYNONYM)",
                """
                SELECT owner, object_name, object_type
                FROM all_objects
                WHERE UPPER(object_name) LIKE '%MDM%'
                  AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
                ORDER BY owner, object_type, object_name
                """,
                limit=40,
            )

            # J2: ALL_OBJECTS con NANSEN en el nombre
            run(
                cur,
                "J2 — ALL_OBJECTS con 'NANSEN' en el nombre",
                """
                SELECT owner, object_name, object_type
                FROM all_objects
                WHERE UPPER(object_name) LIKE '%NANSEN%'
                  AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
                ORDER BY owner, object_type, object_name
                """,
                limit=30,
            )

            # J3: ALL_OBJECTS con INTERV, HORARI, INTERVALO, MINUTE, QUARTER en nombre
            run(
                cur,
                "J3 — ALL_OBJECTS con INTERV / HORARI / MINUTE / QUARTER en el nombre",
                """
                SELECT owner, object_name, object_type
                FROM all_objects
                WHERE (UPPER(object_name) LIKE '%INTERV%'
                    OR UPPER(object_name) LIKE '%HORARI%'
                    OR UPPER(object_name) LIKE '%MINUTE%'
                    OR UPPER(object_name) LIKE '%QUARTER%'
                    OR UPPER(object_name) LIKE '%CUARTO%')
                  AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
                ORDER BY owner, object_type, object_name
                """,
                limit=40,
            )

            # J4: Schemas con más tablas (detectar schema MDM nuevo)
            run(
                cur,
                "J4 — Schemas accesibles con tablas (ordenado por cantidad, top 30)",
                """
                SELECT owner, COUNT(*) AS n_tablas
                FROM all_objects
                WHERE object_type IN ('TABLE', 'VIEW')
                  AND owner NOT IN ('SYS','SYSTEM','OUTLN','DBSNMP','WMSYS',
                                    'APEX_040200','MDSYS','CTXSYS','XDB',
                                    'ORDSYS','ORDPLUGINS','SI_INFORMTN_SCHEMA',
                                    'ANONYMOUS','APPQOSSYS','DVSYS','FLOWS_FILES',
                                    'LBACSYS','OJVMSYS','ORDDATA','OWBSYS',
                                    'SCOTT','SPATIAL_CSW_ADMIN_USR')
                GROUP BY owner
                ORDER BY n_tablas DESC
                FETCH FIRST 30 ROWS ONLY
                """,
                limit=30,
            )

            # J5: Tablas XXSIGEC con PERFIL, TELEMED, HORARI, LECT en el nombre
            run(
                cur,
                "J5 — Tablas/vistas XXSIGEC con PERFIL / TELEMED / HORARI / CUART / MINUT",
                """
                SELECT owner, object_name, object_type
                FROM all_objects
                WHERE owner = 'XXSIGEC'
                  AND (UPPER(object_name) LIKE '%PERFIL%'
                    OR UPPER(object_name) LIKE '%TELEMED%'
                    OR UPPER(object_name) LIKE '%HORARI%'
                    OR UPPER(object_name) LIKE '%CUART%'
                    OR UPPER(object_name) LIKE '%MINUT%'
                    OR UPPER(object_name) LIKE '%INTERV%'
                    OR UPPER(object_name) LIKE '%QUARTER%')
                  AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
                ORDER BY object_name
                """,
                limit=30,
            )

            # J6: XXCONSTELE.M_METERS — ¿tiene nuestro medidor en algún formato?
            run(
                cur,
                "J6 — XXCONSTELE.M_METERS: buscar medidor '91013486' en todas las variantes",
                """
                SELECT *
                FROM XXCONSTELE.M_METERS
                WHERE METER_NO IN ('91013486','091013486','0091013486','91013496')
                   OR UPPER(TO_CHAR(METER_NO)) LIKE '%91013486%'
                FETCH FIRST 10 ROWS ONLY
                """,
                limit=10,
            )

            # J7: M_METERS muestra libre — ver formato real de METER_NO
            run(
                cur,
                "J7 — XXCONSTELE.M_METERS muestra libre (10 filas — formato METER_NO)",
                """
                SELECT *
                FROM XXCONSTELE.M_METERS
                FETCH FIRST 10 ROWS ONLY
                """,
                limit=10,
            )

            # J8: Tablas GEOREF con METER, PROFILE, DATA, READ, NANSEN en nombre
            run(
                cur,
                "J8 — Tablas GEOREF con METER / PROFILE / DATA / READ / LOAD en nombre",
                """
                SELECT owner, object_name, object_type
                FROM all_objects
                WHERE owner = 'GEOREF'
                  AND (UPPER(object_name) LIKE '%METER%'
                    OR UPPER(object_name) LIKE '%PROFIL%'
                    OR UPPER(object_name) LIKE '%DATA%'
                    OR UPPER(object_name) LIKE '%READ%'
                    OR UPPER(object_name) LIKE '%LOAD%')
                  AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
                ORDER BY object_name
                """,
                limit=40,
            )

            # J9: Buscar SNs con formato 91XXXXXX en QUERY_ASSET_METER
            run(
                cur,
                "J9 — QUERY_ASSET_METER: SNs con '00009' que no sean '000090000' (formato NANSEN?)",
                """
                SELECT ID, SN, NAME, MAC
                FROM GEOREF.QUERY_ASSET_METER
                WHERE SN LIKE '00009%'
                  AND SN NOT LIKE '000090000%'
                FETCH FIRST 10 ROWS ONLY
                """,
                limit=10,
            )

            # J10: XXCONSTELE — todos los objetos para detectar tablas de perfil
            run(
                cur,
                "J10 — XXCONSTELE: todos los objetos (TABLE/VIEW) accesibles",
                """
                SELECT owner, object_name, object_type
                FROM all_objects
                WHERE owner = 'XXCONSTELE'
                  AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
                ORDER BY object_type, object_name
                """,
                limit=60,
            )

            # J11: Buscar medidor '91013486' en tabla XXSIGEC.XXCO_LECTURAS_TELEMEDIDAS
            #       ya confirmada — ver si hay lecturas con hora (no solo diarias)
            run(
                cur,
                "J11 — XXCO_LECTURAS_TELEMEDIDAS para '91013486': ver granularidad real de LEC_FECHA_LECTURA",
                """
                SELECT MED_CODIGO, CDR_CODIGO,
                       LEC_FECHA_LECTURA,
                       TO_CHAR(LEC_FECHA_LECTURA, 'YYYY-MM-DD HH24:MI:SS') AS fecha_con_hora,
                       LEC_VALOR_LEIDO
                FROM XXSIGEC.XXCO_LECTURAS_TELEMEDIDAS
                WHERE MED_CODIGO = '91013486'
                  AND CDR_CODIGO = 'E'
                ORDER BY LEC_FECHA_LECTURA DESC
                FETCH FIRST 20 ROWS ONLY
                """,
                limit=20,
            )

            # J12: Buscar en ALL_TABLES (no ALL_OBJECTS) tablas con LECTURAS
            #      en schemas que no hemos explorado
            run(
                cur,
                "J12 — ALL_TABLES con 'LECTURA' en nombre (todos los schemas)",
                """
                SELECT owner, table_name
                FROM all_tables
                WHERE UPPER(table_name) LIKE '%LECTURA%'
                  AND owner NOT IN ('SYS','SYSTEM')
                ORDER BY owner, table_name
                """,
                limit=40,
            )

    finally:
        conn.rollback()
        conn.close()

    print("=" * 72)
    print("  SPIKE LISTADO+NANSEN COMPLETADO")
    print("=" * 72)


if __name__ == "__main__":
    main()
