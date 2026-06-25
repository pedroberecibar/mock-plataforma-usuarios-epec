"""Spike v2: exploración amplia de tablas de perfiles en Oracle.

NO MODIFICA NADA. Solo SELECT. Requiere Oracle configurado en .env

Uso:
    uv run python scripts/spike_perfiles_oracle.py
    uv run python scripts/spike_perfiles_oracle.py --equipo 91013496
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# ── bootstrap ──────────────────────────────────────────────────────────────
_root = Path(__file__).parent.parent
_env_path = _root / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

sys.path.insert(0, str(_root / "src"))

import oracledb  # noqa: E402, I001

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


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE A — Objetos con "PROF" en el nombre (todas las vistas/tablas)
# ═══════════════════════════════════════════════════════════════════════════


def explorar_objetos_prof(cur: oracledb.Cursor) -> None:
    run(
        cur,
        "A1 — Objetos con PROF en el nombre (owner, nombre, tipo)",
        """
        SELECT owner, object_name, object_type
        FROM all_objects
        WHERE UPPER(object_name) LIKE '%PROF%'
        ORDER BY owner, object_type, object_name
        """,
        limit=60,
    )


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE B — Objetos del schema GEOREF
# ═══════════════════════════════════════════════════════════════════════════


def explorar_georef(cur: oracledb.Cursor) -> None:
    run(
        cur,
        "B1 — Todos los objetos de GEOREF accesibles",
        """
        SELECT owner, object_name, object_type
        FROM all_objects
        WHERE UPPER(owner) = 'GEOREF'
        ORDER BY object_type, object_name
        """,
        limit=80,
    )

    run(
        cur,
        "B2 — Objetos GEOREF con ASSET en el nombre",
        """
        SELECT owner, object_name, object_type
        FROM all_objects
        WHERE UPPER(owner) = 'GEOREF'
          AND UPPER(object_name) LIKE '%ASSET%'
        ORDER BY object_type, object_name
        """,
        limit=30,
    )

    run(
        cur,
        "B3 — Columnas de GEOREF.VM_INTELIGENTES (si existe)",
        """
        SELECT column_name, data_type, data_length
        FROM all_tab_columns
        WHERE owner = 'GEOREF' AND table_name = 'VM_INTELIGENTES'
        ORDER BY column_id
        """,
        limit=40,
    )

    run(
        cur,
        "B4 — Columnas de GEOREF.QUERY_ASSET_COMMUNICATOR (si existe)",
        """
        SELECT column_name, data_type, data_length
        FROM all_tab_columns
        WHERE owner = 'GEOREF' AND table_name = 'QUERY_ASSET_COMMUNICATOR'
        ORDER BY column_id
        """,
        limit=40,
    )

    run(
        cur,
        "B5 — Columnas de GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 (si existe)",
        """
        SELECT column_name, data_type, data_length
        FROM all_tab_columns
        WHERE owner = 'GEOREF' AND table_name = 'QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1'
        ORDER BY column_id
        """,
        limit=40,
    )


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE C — Columnas con nombre ID (para entender joins)
# ═══════════════════════════════════════════════════════════════════════════


def explorar_columnas_id(cur: oracledb.Cursor) -> None:
    run(
        cur,
        "C1 — Tablas con columna ID en schemas clave",
        """
        SELECT owner, table_name, data_type
        FROM all_tab_columns
        WHERE column_name = 'ID'
          AND owner IN ('GEOREF','XXCONSTELE','XXSIGEC')
        ORDER BY owner, table_name
        """,
        limit=40,
    )


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE D — Queries directas del usuario
# ═══════════════════════════════════════════════════════════════════════════


def queries_usuario(cur: oracledb.Cursor, equipo: str, suministro: str) -> None:
    # equipo alternativo que el usuario mencionó: 91013486
    equipo_alt = "91013486"

    run(
        cur,
        f"D1 — NUEVA_VISTA_PERFIL para equipo alt {equipo_alt}",
        "SELECT * FROM XXCONSTELE.NUEVA_VISTA_PERFIL WHERE MED_CODIGO = :eq FETCH FIRST 10 ROWS ONLY",
        {"eq": equipo_alt},
    )

    run(
        cur,
        f"D2 — NUEVA_VISTA_PERFIL para equipo {equipo}",
        "SELECT * FROM XXCONSTELE.NUEVA_VISTA_PERFIL WHERE MED_CODIGO = :eq FETCH FIRST 10 ROWS ONLY",
        {"eq": equipo},
    )

    run(
        cur,
        "D3 — GEOREF.QUERY_ASSET_COMMUNICATOR (muestra libre)",
        "SELECT * FROM GEOREF.QUERY_ASSET_COMMUNICATOR FETCH FIRST 5 ROWS ONLY",
    )

    run(
        cur,
        "D4 — GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 (muestra libre)",
        "SELECT * FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 FETCH FIRST 5 ROWS ONLY",
    )

    run(
        cur,
        f"D5 — GEOREF.VM_INTELIGENTES para suministro {suministro}",
        "SELECT * FROM GEOREF.VM_INTELIGENTES WHERE SUMINISTRO = :srv FETCH FIRST 10 ROWS ONLY",
        {"srv": suministro},
    )

    run(
        cur,
        "D5b — GEOREF.VM_INTELIGENTES muestra libre (5 filas)",
        "SELECT * FROM GEOREF.VM_INTELIGENTES FETCH FIRST 5 ROWS ONLY",
    )

    run(
        cur,
        f"D6 — XXSIGEC.XXCO_LECTURAS_TELEMEDIDAS para MED_CODIGO={equipo_alt} (últimas 5)",
        """
        SELECT * FROM xxsigec.xxco_lecturas_telemedidas
        WHERE MED_CODIGO = :eq
        ORDER BY LEC_FECHA_LECTURA DESC
        FETCH FIRST 5 ROWS ONLY
        """,
        {"eq": equipo_alt},
    )

    run(
        cur,
        "D6b — Columnas de XXSIGEC.XXCO_LECTURAS_TELEMEDIDAS",
        """
        SELECT column_name, data_type, data_length
        FROM all_tab_columns
        WHERE owner = 'XXSIGEC' AND table_name = 'XXCO_LECTURAS_TELEMEDIDAS'
        ORDER BY column_id
        """,
        limit=30,
    )


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE E — Exploración extra: XXCONSTELE completo + link con SIGEC
# ═══════════════════════════════════════════════════════════════════════════


def explorar_xxconstele(cur: oracledb.Cursor, equipo: str) -> None:
    run(
        cur,
        "E1 — Todos los objetos de XXCONSTELE accesibles",
        """
        SELECT owner, object_name, object_type
        FROM all_objects
        WHERE UPPER(owner) = 'XXCONSTELE'
        ORDER BY object_type, object_name
        """,
        limit=60,
    )

    run(
        cur,
        "E2 — Columnas de XXCONSTELE.NUEVA_VISTA_PERFIL",
        """
        SELECT column_name, data_type, data_length
        FROM all_tab_columns
        WHERE owner = 'XXCONSTELE' AND table_name = 'NUEVA_VISTA_PERFIL'
        ORDER BY column_id
        """,
        limit=30,
    )

    run(
        cur,
        "E3 — Columnas de XXCONSTELE.VISTA_PERFIL",
        """
        SELECT column_name, data_type, data_length
        FROM all_tab_columns
        WHERE owner = 'XXCONSTELE' AND table_name = 'VISTA_PERFIL'
        ORDER BY column_id
        """,
        limit=30,
    )

    run(
        cur,
        "E4 — Muestra libre NUEVA_VISTA_PERFIL (cualquier fila reciente, EAD)",
        """
        SELECT * FROM XXCONSTELE.NUEVA_VISTA_PERFIL
        WHERE CDR_CODIGO = 'EAD'
          AND LEC_FECHA_LECTURA >= SYSDATE - 7
        FETCH FIRST 10 ROWS ONLY
        """,
    )

    run(
        cur,
        "E5 — Equipos distintos con datos en NUEVA_VISTA_PERFIL (últimos 7 días)",
        """
        SELECT DISTINCT MED_CODIGO
        FROM XXCONSTELE.NUEVA_VISTA_PERFIL
        WHERE CDR_CODIGO = 'EAD'
          AND LEC_FECHA_LECTURA >= SYSDATE - 7
        FETCH FIRST 20 ROWS ONLY
        """,
        limit=20,
    )

    run(
        cur,
        "E6 — CDR_CODIGO distintos en NUEVA_VISTA_PERFIL",
        """
        SELECT DISTINCT CDR_CODIGO, COUNT(*) AS n
        FROM XXCONSTELE.NUEVA_VISTA_PERFIL
        WHERE LEC_FECHA_LECTURA >= SYSDATE - 3
        GROUP BY CDR_CODIGO
        ORDER BY n DESC
        """,
        limit=20,
    )

    # Columnas reales de EQUIPOS
    run(
        cur,
        "E7 — Columnas reales de XXSIGEC.EQUIPOS",
        """
        SELECT column_name, data_type, data_length
        FROM all_tab_columns
        WHERE owner = 'XXSIGEC' AND table_name = 'EQUIPOS'
        ORDER BY column_id
        """,
        limit=40,
    )

    run(
        cur,
        f"E8 — Link: equipo {equipo} en XXSIGEC.EQUIPOS",
        """
        SELECT *
        FROM xxsigec.EQUIPOS
        WHERE STE_NUMERO = :eq
        FETCH FIRST 5 ROWS ONLY
        """,
        {"eq": equipo},
    )


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE F — Si encontramos un equipo con datos, analizar semántica del valor
# ═══════════════════════════════════════════════════════════════════════════


def analizar_semantica(cur: oracledb.Cursor, med_codigo_con_datos: str) -> None:
    """Toma lecturas consecutivas de un equipo que SÍ tiene datos y determina
    si el valor es incremental (kWh de la ventana) o acumulado (contador)."""
    rows = run(
        cur,
        f"F1 — 30 lecturas EAD consecutivas para equipo {med_codigo_con_datos}",
        """
        SELECT MED_CODIGO, LEC_FECHA_LECTURA, LEC_VALOR_LEIDO, CDR_CODIGO
        FROM XXCONSTELE.NUEVA_VISTA_PERFIL
        WHERE MED_CODIGO = :eq
          AND CDR_CODIGO = 'EAD'
        ORDER BY LEC_FECHA_LECTURA
        FETCH FIRST 30 ROWS ONLY
        """,
        {"eq": med_codigo_con_datos},
        limit=30,
    )

    if len(rows) < 3:
        print("  (sin datos suficientes para análisis de semántica)\n")
        return

    # Columna LEC_VALOR_LEIDO está en posición 2
    valores = [float(r[2]) for r in rows if r[2] is not None]
    fechas = [r[1] for r in rows if r[2] is not None]

    if len(valores) < 3:
        return

    diffs = [valores[i + 1] - valores[i] for i in range(len(valores) - 1)]

    print(f"  Valores (primeros 10): {[round(v, 4) for v in valores[:10]]}")
    print(f"  Diffs entre consecutivos: {[round(d, 4) for d in diffs[:10]]}")
    print(f"  Min valor: {min(valores):.4f}   Max valor: {max(valores):.4f}")
    print(f"  Min diff:  {min(diffs):.4f}    Max diff:  {max(diffs):.4f}")
    print(
        f"  Negativos: {sum(1 for d in diffs if d < 0)}  /  Positivos: {sum(1 for d in diffs if d >= 0)}"
    )

    # Intervalo entre lecturas
    if len(fechas) >= 2 and fechas[0] and fechas[1]:
        delta = fechas[1] - fechas[0]
        minutos = delta.total_seconds() / 60 if hasattr(delta, "total_seconds") else "?"
        print(f"  Intervalo entre primeras 2 lecturas: {minutos} minutos")

    if max(valores) > 10_000:
        print("\n  >>> CONCLUSION: ACUMULADO — valores > 10.000, típico de contador")
    elif max(diffs) < 5.0 and min(diffs) >= 0:
        print("\n  >>> CONCLUSION: INCREMENTAL — diffs pequeños y positivos (kWh por ventana)")
    elif min(diffs) < 0:
        print("\n  >>> CONCLUSION: AMBIGUO — hay diffs negativos (resets o errores)")
    else:
        print("\n  >>> CONCLUSION: REVISAR MANUALMENTE")

    print()


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE G — Join VM_INTELIGENTES → SHENYU1: confirmar query real
# ═══════════════════════════════════════════════════════════════════════════

_EQUIPO_NANSEN = "91013486"
_SUMINISTRO_NANSEN = "2817670"


def explorar_shenyu_join(cur: oracledb.Cursor) -> None:
    """Confirma el join correcto suministro → medidor → perfil 15-min."""

    # G1: Todas las columnas de SHENYU1 (incluyendo CHANNEL si existe)
    run(
        cur,
        "G1 — Columnas completas de GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1",
        """
        SELECT column_name, data_type, data_length
        FROM all_tab_columns
        WHERE owner = 'GEOREF' AND table_name = 'QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1'
        ORDER BY column_id
        """,
        limit=50,
    )

    # G2: Muestra raw de SHENYU1 filtrada por EQUIPID = nuestro medidor
    run(
        cur,
        f"G2 — SHENYU1 filtrada por EQUIPID={_EQUIPO_NANSEN!r} (5 filas raw)",
        """
        SELECT *
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1
        WHERE EQUIPID = :eq
        FETCH FIRST 5 ROWS ONLY
        """,
        {"eq": _EQUIPO_NANSEN},
        limit=5,
    )

    # G3: ¿Qué formato tiene PERIODI? Ver largo y un ejemplo
    run(
        cur,
        "G3 — Formato de PERIODI: longitud y ejemplo para nuestro medidor",
        """
        SELECT
          PERIODI,
          LENGTH(PERIODI) AS largo,
          SUBSTR(PERIODI, 1, 8)  AS parte_fecha,
          SUBSTR(PERIODI, 9, 4)  AS parte_hora_min,
          SUBSTR(PERIODI, 13)    AS resto
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1
        WHERE EQUIPID = :eq
        FETCH FIRST 5 ROWS ONLY
        """,
        {"eq": _EQUIPO_NANSEN},
        limit=5,
    )

    # G4: Filas por día para nuestro medidor (últimos 7 días)
    run(
        cur,
        f"G4 — Filas/día en SHENYU1 para equipo {_EQUIPO_NANSEN!r} (últimos 7 días)",
        """
        SELECT
          SUBSTR(PERIODI, 1, 8)    AS fecha_dia,
          COUNT(*)                 AS n_filas,
          COUNT(*) * 12            AS periodos_15min_max
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1
        WHERE EQUIPID = :eq
          AND PERIODI >= TO_CHAR(SYSDATE - 7, 'YYYYMMDD') || '0000'
        GROUP BY SUBSTR(PERIODI, 1, 8)
        ORDER BY fecha_dia DESC
        """,
        {"eq": _EQUIPO_NANSEN},
        limit=10,
    )

    # G5: JOIN completo suministro → VM_INTELIGENTES → SHENYU1
    run(
        cur,
        f"G5 — JOIN suministro {_SUMINISTRO_NANSEN} → VM_INTELIGENTES → SHENYU1 (10 filas)",
        """
        SELECT
          v.suministro,
          v.medidor,
          s.PERIODI,
          s.VALUE3
        FROM GEOREF.VM_INTELIGENTES v
        JOIN GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 s
          ON s.EQUIPID = v.medidor
        WHERE v.suministro = :srv
          AND s.PERIODI >= TO_CHAR(SYSDATE - 3, 'YYYYMMDD') || '0000'
        FETCH FIRST 10 ROWS ONLY
        """,
        {"srv": _SUMINISTRO_NANSEN},
        limit=10,
    )

    # G6: Unpivot VALUE1-VALUE12 en filas individuales (CONNECT BY) — 1 día
    run(
        cur,
        f"G6 — Unpivot SHENYU1 en 15-min para equipo {_EQUIPO_NANSEN!r} (1 día reciente, 20 filas)",
        """
        SELECT
          s.PERIODI,
          (LEVEL - 1) * 15   AS minuto_offset,
          CASE LEVEL
            WHEN  1 THEN TO_NUMBER(s.VALUE1)
            WHEN  2 THEN TO_NUMBER(s.VALUE2)
            WHEN  3 THEN TO_NUMBER(s.VALUE3)
            WHEN  4 THEN TO_NUMBER(s.VALUE4)
            WHEN  5 THEN TO_NUMBER(s.VALUE5)
            WHEN  6 THEN TO_NUMBER(s.VALUE6)
            WHEN  7 THEN TO_NUMBER(s.VALUE7)
            WHEN  8 THEN TO_NUMBER(s.VALUE8)
            WHEN  9 THEN TO_NUMBER(s.VALUE9)
            WHEN 10 THEN TO_NUMBER(s.VALUE10)
            WHEN 11 THEN TO_NUMBER(s.VALUE11)
            WHEN 12 THEN TO_NUMBER(s.VALUE12)
          END                AS kwh_15min
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 s
        CROSS JOIN (SELECT LEVEL FROM DUAL CONNECT BY LEVEL <= 12)
        WHERE s.EQUIPID = :eq
          AND s.PERIODI >= TO_CHAR(SYSDATE - 1, 'YYYYMMDD') || '0000'
          AND s.PERIODI <  TO_CHAR(SYSDATE - 0, 'YYYYMMDD') || '0000'
        ORDER BY s.PERIODI, LEVEL
        FETCH FIRST 20 ROWS ONLY
        """,
        {"eq": _EQUIPO_NANSEN},
        limit=20,
    )

    # G7: CHANNEL — ¿existe esa columna en SHENYU1?
    run(
        cur,
        "G7 — Valores distintos de CHANNEL en SHENYU1 (si la columna existe)",
        """
        SELECT CHANNEL, COUNT(*) AS n
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1
        WHERE PERIODI >= TO_CHAR(SYSDATE - 3, 'YYYYMMDD') || '0000'
        GROUP BY CHANNEL
        ORDER BY n DESC
        """,
        limit=20,
    )

    # G8: ¿SHENYU2 tiene el mismo medidor? Comparar
    run(
        cur,
        f"G8 — SHENYU2 filtrada por EQUIPID={_EQUIPO_NANSEN!r} (5 filas)",
        """
        SELECT *
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU2
        WHERE EQUIPID = :eq
        FETCH FIRST 5 ROWS ONLY
        """,
        {"eq": _EQUIPO_NANSEN},
        limit=5,
    )

    # G9: ¿NUEVA_VISTA_PERFIL tiene al medidor con ceros a la izquierda?
    run(
        cur,
        "G9 — NUEVA_VISTA_PERFIL con MED_CODIGO='091013486' (con cero) y variantes",
        """
        SELECT MED_CODIGO, COUNT(*) AS n
        FROM XXCONSTELE.NUEVA_VISTA_PERFIL
        WHERE MED_CODIGO IN ('91013486', '091013486', '0091013486', '91013496', '091013496')
        GROUP BY MED_CODIGO
        """,
        limit=10,
    )


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE H — Corrige nombres de columna: DEVICE_ID + TV (no EQUIPID/PERIODI)
# ═══════════════════════════════════════════════════════════════════════════


def explorar_shenyu_corregido(cur: oracledb.Cursor) -> None:
    """Mismas preguntas que G pero con los nombres reales: DEVICE_ID y TV."""

    # H1: Muestra libre SHENYU1 sin filtro (ver DEVICE_ID real y formato de TV)
    run(
        cur,
        "H1 — SHENYU1 muestra libre (5 filas, ver DEVICE_ID y TV)",
        """
        SELECT DEVICE_ID, TV, UPDATE_TV, VALUE1, VALUE2, VALUE3, VALUE4
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1
        FETCH FIRST 5 ROWS ONLY
        """,
        limit=5,
    )

    # H2: DEVICE_ID distintos con datos recientes
    run(
        cur,
        "H2 — DEVICE_ID distintos en SHENYU1 (TV >= hoy-7, hasta 20)",
        """
        SELECT DISTINCT DEVICE_ID
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1
        WHERE TV >= SYSDATE - 7
        FETCH FIRST 20 ROWS ONLY
        """,
        limit=20,
    )

    # H3: SHENYU1 filtrada por DEVICE_ID = nuestro medidor
    run(
        cur,
        f"H3 — SHENYU1 WHERE DEVICE_ID={_EQUIPO_NANSEN!r} (10 filas)",
        """
        SELECT DEVICE_ID, TV, VALUE1, VALUE2, VALUE3, VALUE4
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1
        WHERE DEVICE_ID = :eq
        FETCH FIRST 10 ROWS ONLY
        """,
        {"eq": _EQUIPO_NANSEN},
        limit=10,
    )

    # H4: Filas por dia usando TV (DATE) — nuestro medidor, ultimos 7 dias
    run(
        cur,
        f"H4 — Filas/dia SHENYU1 para DEVICE_ID={_EQUIPO_NANSEN!r} (TV >= hoy-7)",
        """
        SELECT
          TRUNC(TV)          AS fecha_dia,
          COUNT(*)           AS n_filas,
          COUNT(*) * 12      AS periodos_15min_max
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1
        WHERE DEVICE_ID = :eq
          AND TV >= SYSDATE - 7
        GROUP BY TRUNC(TV)
        ORDER BY fecha_dia DESC
        """,
        {"eq": _EQUIPO_NANSEN},
        limit=10,
    )

    # H5: JOIN corregido suministro -> VM_INTELIGENTES -> SHENYU1 via DEVICE_ID=medidor
    run(
        cur,
        f"H5 — JOIN suministro {_SUMINISTRO_NANSEN} -> VM_INTELIGENTES -> SHENYU1 (10 filas)",
        """
        SELECT
          v.suministro,
          v.medidor,
          s.TV,
          s.VALUE3
        FROM GEOREF.VM_INTELIGENTES v
        JOIN GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 s
          ON s.DEVICE_ID = v.medidor
        WHERE v.suministro = :srv
          AND s.TV >= SYSDATE - 3
        FETCH FIRST 10 ROWS ONLY
        """,
        {"srv": _SUMINISTRO_NANSEN},
        limit=10,
    )

    # H6: Unpivot VALUE1-VALUE12 en 12 filas de 15 min usando TV como base
    run(
        cur,
        f"H6 — Unpivot SHENYU1 en 15-min para {_EQUIPO_NANSEN!r} (TV >= hoy-1, 20 filas)",
        """
        SELECT
          s.DEVICE_ID,
          s.TV + (n.lvl - 1) * 15 / 1440   AS ts_15min,
          (n.lvl - 1) * 15                  AS minuto_offset,
          CASE n.lvl
            WHEN  1 THEN TO_NUMBER(s.VALUE1)
            WHEN  2 THEN TO_NUMBER(s.VALUE2)
            WHEN  3 THEN TO_NUMBER(s.VALUE3)
            WHEN  4 THEN TO_NUMBER(s.VALUE4)
            WHEN  5 THEN TO_NUMBER(s.VALUE5)
            WHEN  6 THEN TO_NUMBER(s.VALUE6)
            WHEN  7 THEN TO_NUMBER(s.VALUE7)
            WHEN  8 THEN TO_NUMBER(s.VALUE8)
            WHEN  9 THEN TO_NUMBER(s.VALUE9)
            WHEN 10 THEN TO_NUMBER(s.VALUE10)
            WHEN 11 THEN TO_NUMBER(s.VALUE11)
            WHEN 12 THEN TO_NUMBER(s.VALUE12)
          END                               AS kwh_15min
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 s
        CROSS JOIN (
          SELECT LEVEL AS lvl FROM DUAL CONNECT BY LEVEL <= 12
        ) n
        WHERE s.DEVICE_ID = :eq
          AND s.TV >= SYSDATE - 1
        ORDER BY s.TV, n.lvl
        FETCH FIRST 20 ROWS ONLY
        """,
        {"eq": _EQUIPO_NANSEN},
        limit=20,
    )

    # H7: Verificar si VM_INTELIGENTES.medidor coincide con SHENYU1.DEVICE_ID directamente
    run(
        cur,
        f"H7 — VM_INTELIGENTES para suministro {_SUMINISTRO_NANSEN}: ver formato de medidor",
        """
        SELECT suministro, medidor, LENGTH(medidor) AS largo_medidor
        FROM GEOREF.VM_INTELIGENTES
        WHERE suministro = :srv
        """,
        {"srv": _SUMINISTRO_NANSEN},
        limit=10,
    )

    # H8: SHENYU2 con DEVICE_ID corregido
    run(
        cur,
        f"H8 — SHENYU2 WHERE DEVICE_ID={_EQUIPO_NANSEN!r} (5 filas)",
        """
        SELECT DEVICE_ID, TV, VALUE1, VALUE2, VALUE3
        FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU2
        WHERE DEVICE_ID = :eq
        FETCH FIRST 5 ROWS ONLY
        """,
        {"eq": _EQUIPO_NANSEN},
        limit=5,
    )


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE I — QUERY_ASSET_METER: verificar medidores 70XXXXXX del listado
# ═══════════════════════════════════════════════════════════════════════════

# Muestra de medidores del listado-mi-activos.md (serie 70XXXXXX — probablemente CLOU)
_MUESTRA_LISTADO_70 = [
    "70096469",
    "70096451",
    "70096527",
    "70096463",
    "70096530",
    "70085039",
    "70084821",
    "70099630",
]
# Muestra de medidores del listado serie 90008XXX
_MUESTRA_LISTADO_90008 = [
    "90008989",
    "90008245",
    "90008983",
    "90008578",
    "90008384",
]
# Muestra de medidores del listado serie 90010XXX
_MUESTRA_LISTADO_90010 = [
    "90010533",
    "90010551",
    "90010537",
    "90010532",
    "90010469",
]


def explorar_listado_en_query_asset_meter(cur: oracledb.Cursor) -> None:
    """Verifica si los medidores del listado están en GEOREF.QUERY_ASSET_METER."""

    # I1: Distinct TELEMEDIBLE en VM_INTELIGENTES (pedido explícito del usuario)
    run(
        cur,
        "I1 — SELECT DISTINCT(TELEMEDIBLE) FROM GEOREF.VM_INTELIGENTES WHERE TELEMEDIBLE IS NOT NULL",
        """
        SELECT TELEMEDIBLE, COUNT(*) AS n
        FROM GEOREF.VM_INTELIGENTES
        WHERE TELEMEDIBLE IS NOT NULL
        GROUP BY TELEMEDIBLE
        ORDER BY n DESC
        """,
        limit=20,
    )

    # I2: SELECT * FROM VM_INTELIGENTES (muestra 3 filas — ver todas las columnas con datos reales)
    run(
        cur,
        "I2 — SELECT * FROM GEOREF.VM_INTELIGENTES FETCH FIRST 3 ROWS ONLY",
        """
        SELECT *
        FROM GEOREF.VM_INTELIGENTES
        FETCH FIRST 3 ROWS ONLY
        """,
        limit=3,
    )

    # I3: Lista de columnas de VM_INTELIGENTES con sus tipos
    run(
        cur,
        "I3 — Columnas de GEOREF.VM_INTELIGENTES (nombres, tipos, largo)",
        """
        SELECT column_name, data_type, data_length, nullable
        FROM all_tab_columns
        WHERE owner = 'GEOREF' AND table_name = 'VM_INTELIGENTES'
        ORDER BY column_id
        """,
        limit=120,
    )

    # I4: Buscar medidores 70XXXXXX en QUERY_ASSET_METER (zero-padded a 12 chars)
    sn_list_70 = [f"000{m}" for m in _MUESTRA_LISTADO_70]
    placeholders = ", ".join(f":sn{i}" for i in range(len(sn_list_70)))
    params = {f"sn{i}": sn for i, sn in enumerate(sn_list_70)}
    run(
        cur,
        f"I4 — QUERY_ASSET_METER para {len(sn_list_70)} medidores 70XXXXXX del listado (zero-padded)",
        f"""
        SELECT ID, SN, NAME, MAC
        FROM GEOREF.QUERY_ASSET_METER
        WHERE SN IN ({placeholders})
        """,
        params,
        limit=20,
    )

    # I5: Buscar sin zero-padding (SN como viene en el listado)
    placeholders_raw = ", ".join(f":sn{i}" for i in range(len(_MUESTRA_LISTADO_70)))
    params_raw = {f"sn{i}": sn for i, sn in enumerate(_MUESTRA_LISTADO_70)}
    run(
        cur,
        "I5 — QUERY_ASSET_METER SN sin zero-padding (como está en el listado)",
        f"""
        SELECT ID, SN, NAME, MAC
        FROM GEOREF.QUERY_ASSET_METER
        WHERE SN IN ({placeholders_raw})
        """,
        params_raw,
        limit=20,
    )

    # I6: Buscar medidores 90008XXX en QUERY_ASSET_METER
    sn_list_90008 = [f"000{m}" for m in _MUESTRA_LISTADO_90008]
    placeholders_90 = ", ".join(f":sn{i}" for i in range(len(sn_list_90008)))
    params_90 = {f"sn{i}": sn for i, sn in enumerate(sn_list_90008)}
    run(
        cur,
        f"I6 — QUERY_ASSET_METER para medidores 90008XXX del listado (zero-padded)",
        f"""
        SELECT ID, SN, NAME, MAC
        FROM GEOREF.QUERY_ASSET_METER
        WHERE SN IN ({placeholders_90})
        """,
        params_90,
        limit=10,
    )

    # I7: Confirmar que medidores 70XXXXXX tienen data en SHENYU1
    # Tomar el primer resultado de I4 si lo hay, o usar un SN conocido
    run(
        cur,
        "I7 — SHENYU1: filas recientes para un medidor 70XXXXXX del listado (via QUERY_ASSET_METER join)",
        """
        SELECT q.SN, q.ID AS device_uuid, COUNT(*) AS n_filas, MAX(s.TV) AS ultima_lectura
        FROM GEOREF.QUERY_ASSET_METER q
        JOIN GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 s
          ON s.DEVICE_ID = q.ID
        WHERE q.SN IN ('000070096469', '000070096451', '000070096527',
                       '000070085039', '000070084821', '000070099630')
          AND s.TV >= SYSDATE - 7
        GROUP BY q.SN, q.ID
        ORDER BY n_filas DESC
        FETCH FIRST 5 ROWS ONLY
        """,
        limit=5,
    )


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE J — Buscar tablas de perfiles NANSEN: MDM, INTERV, HORARI, NANSEN
# ═══════════════════════════════════════════════════════════════════════════


def buscar_tablas_nansen(cur: oracledb.Cursor) -> None:
    """Busca en ALL_OBJECTS tablas que puedan contener perfiles de medidores NANSEN."""

    # J1: Objetos con 'MDM' en el nombre (cualquier schema)
    run(
        cur,
        "J1 — ALL_OBJECTS con 'MDM' en el nombre",
        """
        SELECT owner, object_name, object_type
        FROM all_objects
        WHERE UPPER(object_name) LIKE '%MDM%'
          AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
        ORDER BY owner, object_type, object_name
        """,
        limit=40,
    )

    # J2: Objetos con 'NANSEN' en el nombre
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

    # J3: Objetos con 'INTERV' (interval) o 'HORARI' o 'INTERVALO'
    run(
        cur,
        "J3 — ALL_OBJECTS con INTERV / HORARI / INTERVALO en el nombre",
        """
        SELECT owner, object_name, object_type
        FROM all_objects
        WHERE (UPPER(object_name) LIKE '%INTERV%'
            OR UPPER(object_name) LIKE '%HORARI%'
            OR UPPER(object_name) LIKE '%INTERVALO%')
          AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
        ORDER BY owner, object_type, object_name
        """,
        limit=40,
    )

    # J4: Schemas accesibles con objetos de tipo tabla (ver si hay schema MDM/AMI nuevo)
    run(
        cur,
        "J4 — Schemas distintos con tablas accesibles (no SYS/SYSTEM/XXSIGEC conocidos)",
        """
        SELECT owner, COUNT(*) AS n_tablas
        FROM all_objects
        WHERE object_type = 'TABLE'
          AND owner NOT IN ('SYS', 'SYSTEM', 'OUTLN', 'DBSNMP', 'WMSYS',
                            'APEX_040200', 'MDSYS', 'CTXSYS', 'XDB',
                            'ORDSYS', 'ORDPLUGINS', 'SI_INFORMTN_SCHEMA')
        GROUP BY owner
        ORDER BY n_tablas DESC
        FETCH FIRST 30 ROWS ONLY
        """,
        limit=30,
    )

    # J5: Tablas en XXSIGEC con PERFIL/LECTURA/TELEMEDIDA en el nombre
    run(
        cur,
        "J5 — Tablas XXSIGEC con PERFIL, LECTURA, TELEMEDIDA, HORARI en el nombre",
        """
        SELECT owner, object_name, object_type
        FROM all_objects
        WHERE owner = 'XXSIGEC'
          AND (UPPER(object_name) LIKE '%PERFIL%'
            OR UPPER(object_name) LIKE '%LECTUR%'
            OR UPPER(object_name) LIKE '%TELEMED%'
            OR UPPER(object_name) LIKE '%HORARI%'
            OR UPPER(object_name) LIKE '%INTERV%')
          AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
        ORDER BY object_name
        """,
        limit=30,
    )

    # J6: XXCONSTELE.M_METERS — ¿tiene el medidor 91013486 bajo algún formato?
    run(
        cur,
        "J6 — XXCONSTELE.M_METERS para medidor '91013486' (varias variantes)",
        """
        SELECT *
        FROM XXCONSTELE.M_METERS
        WHERE METER_NO IN ('91013486', '091013486', '0091013486')
           OR UTILITY_METER_ID IN ('91013486', '091013486', '0091013486')
        FETCH FIRST 10 ROWS ONLY
        """,
        limit=10,
    )

    # J7: Muestra libre M_METERS para ver el formato de meter_no real
    run(
        cur,
        "J7 — XXCONSTELE.M_METERS muestra libre (10 filas — ver formato de METER_NO)",
        """
        SELECT *
        FROM XXCONSTELE.M_METERS
        FETCH FIRST 10 ROWS ONLY
        """,
        limit=10,
    )

    # J8: Tablas GEOREF con 'METER' o 'PROFILE' o 'DATA' en el nombre
    run(
        cur,
        "J8 — Tablas GEOREF con METER / PROFILE / DATA / READ en el nombre",
        """
        SELECT owner, object_name, object_type
        FROM all_objects
        WHERE owner = 'GEOREF'
          AND (UPPER(object_name) LIKE '%METER%'
            OR UPPER(object_name) LIKE '%PROFIL%'
            OR UPPER(object_name) LIKE '%DATA%'
            OR UPPER(object_name) LIKE '%READ%')
          AND object_type IN ('TABLE', 'VIEW', 'SYNONYM')
        ORDER BY object_name
        """,
        limit=40,
    )

    # J9: VM_INTELIGENTES — ver qué columnas tienen los medidores NANSEN vs CLOU
    run(
        cur,
        "J9 — VM_INTELIGENTES: muestra de medidores NANSEN (TELEMEDIBLE='NANSEN', 5 filas)",
        """
        SELECT suministro, medidor, telemedible, pct, origen_lectura,
               dc_latitud, dc_longitud
        FROM GEOREF.VM_INTELIGENTES
        WHERE UPPER(telemedible) = 'NANSEN'
        FETCH FIRST 5 ROWS ONLY
        """,
        limit=5,
    )

    # J10: VM_INTELIGENTES — muestra de medidores CLOU
    run(
        cur,
        "J10 — VM_INTELIGENTES: muestra de medidores CLOU (TELEMEDIBLE='CLOU', 5 filas)",
        """
        SELECT suministro, medidor, telemedible, pct, origen_lectura,
               dc_latitud, dc_longitud
        FROM GEOREF.VM_INTELIGENTES
        WHERE UPPER(telemedible) = 'CLOU'
        FETCH FIRST 5 ROWS ONLY
        """,
        limit=5,
    )

    # J11: Verificar si medidores NANSEN aparecen en QUERY_ASSET_METER bajo algún formato
    run(
        cur,
        "J11 — QUERY_ASSET_METER: SNs parecidos a formato NANSEN (91XXXXXX → 00091XXXXXX)",
        """
        SELECT ID, SN, NAME, MAC
        FROM GEOREF.QUERY_ASSET_METER
        WHERE SN LIKE '00009%'
          AND SN NOT LIKE '000090000%'
        FETCH FIRST 10 ROWS ONLY
        """,
        limit=10,
    )


# ═══════════════════════════════════════════════════════════════════════════
# main
# ═══════════════════════════════════════════════════════════════════════════


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--equipo", default="91013496")
    parser.add_argument("--suministro", default="2817670")
    args = parser.parse_args()

    print(f"\n{'=' * 72}")
    print(f"  SPIKE v2 — equipo={args.equipo}  suministro={args.suministro}")
    print(f"{'=' * 72}\n")

    conn = _conectar()
    try:
        with conn.cursor() as cur:
            explorar_objetos_prof(cur)
            explorar_georef(cur)
            explorar_columnas_id(cur)
            queries_usuario(cur, args.equipo, args.suministro)
            explorar_xxconstele(cur, args.equipo)

            # Si E5 encuentra equipos con datos, analizar semántica del primero
            print(SEP)
            print("  F0 — Buscando equipo con datos para análisis de semántica...")
            print(SEP)
            try:
                cur.execute(
                    """
                    SELECT MED_CODIGO FROM XXCONSTELE.NUEVA_VISTA_PERFIL
                    WHERE CDR_CODIGO = 'EAD'
                      AND LEC_FECHA_LECTURA >= SYSDATE - 7
                    FETCH FIRST 1 ROWS ONLY
                    """
                )
                row = cur.fetchone()
                if row:
                    med = str(row[0])
                    print(f"  Usando equipo: {med}\n")
                    analizar_semantica(cur, med)
                else:
                    print("  Sin equipos con datos EAD en últimos 7 días.\n")
            except Exception as exc:
                print(f"  ERROR: {exc}\n")

            # Bloque G: join VM_INTELIGENTES → SHENYU1
            print(SEP)
            print("  G0 — Confirmando join GEOREF: suministro → medidor → SHENYU1")
            print(SEP)
            print()
            explorar_shenyu_join(cur)

            # Bloque H: columnas reales DEVICE_ID + TV (correccion de G)
            print(SEP)
            print("  H0 — SHENYU1 con nombres reales DEVICE_ID + TV")
            print(SEP)
            print()
            explorar_shenyu_corregido(cur)

            # Bloque I: verificar medidores del listado en QUERY_ASSET_METER + DISTINCT TELEMEDIBLE
            print(SEP)
            print("  I0 — VM_INTELIGENTES TELEMEDIBLE + medidores listado en QUERY_ASSET_METER")
            print(SEP)
            print()
            explorar_listado_en_query_asset_meter(cur)

            # Bloque J: buscar tablas de perfiles NANSEN
            print(SEP)
            print("  J0 — Buscando tablas de perfiles NANSEN (MDM, INTERV, HORARI, ...)")
            print(SEP)
            print()
            buscar_tablas_nansen(cur)

    finally:
        conn.rollback()
        conn.close()

    print("=" * 72)
    print("  SPIKE v2 COMPLETADO")
    print("=" * 72)


if __name__ == "__main__":
    main()
