"""Spike: explorar tablas de perfiles (lecturas 15-min) en Oracle.

OBJETIVO:
  1. Confirmar acceso a xxconstele.NUEVA_VISTA_PERFIL y xxconstele.VISTA_PERFIL
  2. Confirmar acceso a georef.asset_meter y georef.data_md_profile_minutely_sh1
  3. Determinar si los valores (EAD) son INCREMENTALES o ACUMULADOS
  4. Entender cómo linkear med_codigo → srv_codigo (suministro)
  5. Verificar granularidad real (15 min, 30 min, 1 hora?)

NO MODIFICA NADA. Solo SELECT. Requiere Oracle configurado en .env

Uso:
    uv run python scripts/spike_perfiles_oracle.py
    uv run python scripts/spike_perfiles_oracle.py --equipo 91013496
    uv run python scripts/spike_perfiles_oracle.py --equipo 91013496 --dias 3
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, timedelta
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

SEP = "-" * 70


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


def _tabla_existe(cur: oracledb.Cursor, owner: str, nombre: str) -> bool:
    cur.execute(
        "SELECT COUNT(*) FROM all_tables WHERE owner = :o AND table_name = :t",
        {"o": owner.upper(), "t": nombre.upper()},
    )
    return (cur.fetchone() or [0])[0] > 0


def _vista_existe(cur: oracledb.Cursor, owner: str, nombre: str) -> bool:
    cur.execute(
        "SELECT COUNT(*) FROM all_views WHERE owner = :o AND view_name = :t",
        {"o": owner.upper(), "t": nombre.upper()},
    )
    return (cur.fetchone() or [0])[0] > 0


# ── Sección 1: verificar objetos accesibles ─────────────────────────────────


def verificar_acceso(cur: oracledb.Cursor) -> None:
    print(SEP)
    print("SECCIÓN 1 — Verificar acceso a tablas/vistas")
    print(SEP)

    objetos = [
        ("xxconstele", "NUEVA_VISTA_PERFIL", "vista"),
        ("xxconstele", "VISTA_PERFIL", "vista"),
        ("georef", "ASSET_METER", "tabla"),
        ("georef", "DATA_MD_PROFILE_MINUTELY_SH1", "tabla"),
        ("xxsigec", "XXCO_LECTURAS_TELEMEDIDAS_H", "tabla"),
        ("xxsigec", "EQUIPOS", "tabla"),
    ]

    for owner, nombre, tipo in objetos:
        if tipo == "vista":
            existe = _vista_existe(cur, owner, nombre)
        else:
            existe = _tabla_existe(cur, owner, nombre)
        estado = "✓ ACCESIBLE" if existe else "✗ NO VISIBLE"
        print(f"  {estado}  {owner}.{nombre}")

    print()


# ── Sección 2: columnas de las tablas clave ──────────────────────────────────


def describir_columnas(cur: oracledb.Cursor) -> None:
    print(SEP)
    print("SECCIÓN 2 — Columnas de tablas clave")
    print(SEP)

    queries = [
        ("georef.DATA_MD_PROFILE_MINUTELY_SH1", "georef", "DATA_MD_PROFILE_MINUTELY_SH1", "tabla"),
        ("georef.ASSET_METER", "georef", "ASSET_METER", "tabla"),
        (
            "xxconstele.NUEVA_VISTA_PERFIL (primeras 10 cols)",
            "xxconstele",
            "NUEVA_VISTA_PERFIL",
            "vista",
        ),
    ]

    for label, owner, nombre, tipo in queries:
        print(f"\n  {label}:")
        try:
            table_type = "ALL_TAB_COLUMNS" if tipo == "tabla" else "ALL_TAB_COLUMNS"
            cur.execute(
                f"SELECT column_name, data_type, data_length "
                f"FROM {table_type} "
                f"WHERE owner = :o AND table_name = :t "
                f"ORDER BY column_id",
                {"o": owner.upper(), "t": nombre.upper()},
            )
            rows = cur.fetchmany(20)
            if not rows:
                print("    (sin acceso o no existe)")
            for col_name, data_type, data_length in rows:
                print(f"    {col_name:<35} {data_type}({data_length})")
        except Exception as exc:
            print(f"    ERROR: {exc}")

    print()


# ── Sección 3: muestra de datos de perfiles vía georef ───────────────────────


def muestra_georef(cur: oracledb.Cursor, equipo: str, dias: int) -> None:
    print(SEP)
    print(f"SECCIÓN 3 — Muestra de perfiles vía georef (equipo={equipo}, últimos {dias} días)")
    print(SEP)

    hasta = date.today()
    desde = hasta - timedelta(days=dias)

    try:
        cur.execute(
            """
            SELECT
                mi_am.sn                       AS med_codigo,
                perfil.value3                  AS ead,
                perfil.value5                  AS erq1,
                perfil.tv - ( 15 / 1440 )      AS fecha_desde,
                perfil.tv                      AS fecha_hasta
            FROM
                georef.asset_meter                  mi_am,
                georef.data_md_profile_minutely_sh1 perfil
            WHERE
                    perfil.device_id = mi_am.id
                AND mi_am.sn = :medidor
                AND perfil.tv >= :fecha_min
                AND perfil.tv <  :fecha_max
            ORDER BY perfil.tv
            FETCH FIRST 20 ROWS ONLY
            """,
            {"medidor": equipo, "fecha_min": desde, "fecha_max": hasta},
        )
        rows = cur.fetchall()
        if not rows:
            print("  Sin datos para ese equipo/rango.\n")
            return

        cols = [d[0].lower() for d in cur.description]
        print(f"  Columnas: {cols}")
        print(f"  Primeras {len(rows)} filas:\n")
        for row in rows:
            print(f"  {dict(zip(cols, row, strict=False))}")

        # Análisis: ¿incremental o acumulado?
        _analizar_incremento(rows, cols)

    except Exception as exc:
        print(f"  ERROR en consulta georef: {exc}")

    print()


# ── Sección 4: muestra vía NUEVA_VISTA_PERFIL ────────────────────────────────


def muestra_vista_perfil(cur: oracledb.Cursor, equipo: str, dias: int) -> None:
    print(SEP)
    print(f"SECCIÓN 4 — Muestra vía xxconstele.NUEVA_VISTA_PERFIL (equipo={equipo})")
    print(SEP)

    hasta = date.today()
    desde = hasta - timedelta(days=dias)

    try:
        cur.execute(
            """
            SELECT
                vp.med_codigo,
                vp.lec_fecha_lectura                 AS fecha_desde,
                vp.lec_fecha_lectura + ( 15 / 1440 ) AS fecha_hasta,
                vp.lec_valor_leido                   AS valor_leido,
                vp.cdr_codigo                        AS cdr_unidad
            FROM
                xxconstele.nueva_vista_perfil vp
            WHERE
                    vp.cdr_codigo IN ( 'EAD', 'ERQ1' )
                AND vp.med_codigo = :med_codigo
                AND vp.lec_fecha_lectura >= :fecha_min
                AND vp.lec_fecha_lectura <  :fecha_max
            ORDER BY vp.lec_fecha_lectura
            FETCH FIRST 20 ROWS ONLY
            """,
            {"med_codigo": equipo, "fecha_min": desde, "fecha_max": hasta},
        )
        rows = cur.fetchall()
        if not rows:
            print("  Sin datos para ese equipo/rango.\n")
            return

        cols = [d[0].lower() for d in cur.description]
        print(f"  Columnas: {cols}")
        print(f"  Primeras {len(rows)} filas:\n")
        for row in rows:
            print(f"  {dict(zip(cols, row, strict=False))}")

        _analizar_incremento(rows, cols)

    except Exception as exc:
        print(f"  ERROR en consulta nueva_vista_perfil: {exc}")

    print()


# ── Sección 5: granularidad real ─────────────────────────────────────────────


def verificar_granularidad(cur: oracledb.Cursor, equipo: str) -> None:
    print(SEP)
    print(f"SECCIÓN 5 — Granularidad real de los datos (equipo={equipo})")
    print(SEP)

    hasta = date.today()
    desde = hasta - timedelta(days=3)

    try:
        # Calcula los intervalos entre lecturas consecutivas (en minutos)
        cur.execute(
            """
            SELECT
                ROUND(
                    (perfil.tv - LAG(perfil.tv) OVER (ORDER BY perfil.tv)) * 1440,
                    2
                ) AS intervalo_minutos,
                COUNT(*) AS cantidad
            FROM
                georef.asset_meter mi_am,
                georef.data_md_profile_minutely_sh1 perfil
            WHERE
                    perfil.device_id = mi_am.id
                AND mi_am.sn = :medidor
                AND perfil.tv >= :fecha_min
                AND perfil.tv <  :fecha_max
            GROUP BY
                ROUND(
                    (perfil.tv - LAG(perfil.tv) OVER (ORDER BY perfil.tv)) * 1440,
                    2
                )
            ORDER BY cantidad DESC
            FETCH FIRST 10 ROWS ONLY
            """,
            {"medidor": equipo, "fecha_min": desde, "fecha_max": hasta},
        )
        rows = cur.fetchall()
        if not rows:
            print("  Sin datos para calcular granularidad.")
        else:
            print("  Intervalos más frecuentes entre lecturas consecutivas:")
            for intervalo, cantidad in rows:
                print(f"    {intervalo} minutos → {cantidad} ocurrencias")
    except Exception as exc:
        print(f"  ERROR calculando granularidad: {exc}")

    print()


# ── Sección 6: link med_codigo → srv_codigo ──────────────────────────────────


def verificar_link_srv(cur: oracledb.Cursor, equipo: str) -> None:
    print(SEP)
    print(f"SECCIÓN 6 — Linkeo med_codigo ({equipo}) → srv_codigo")
    print(SEP)

    # Intento 1: via EQUIPOS (campo STE_NUMERO = med_numero_equipo ≈ sn)
    try:
        cur.execute(
            """
            SELECT e.SRV_CODIGO, e.STE_NUMERO, e.STE_CODIGO_TIPO
            FROM xxsigec.EQUIPOS e
            WHERE e.STE_NUMERO = :eq
            FETCH FIRST 5 ROWS ONLY
            """,
            {"eq": equipo},
        )
        rows = cur.fetchall()
        print("  Vía xxsigec.EQUIPOS (STE_NUMERO = med_codigo):")
        if rows:
            for row in rows:
                print(f"    srv_codigo={row[0]}, ste_numero={row[1]}, tipo={row[2]}")
        else:
            print("    Sin resultados")
    except Exception as exc:
        print(f"  ERROR en EQUIPOS: {exc}")

    # Intento 2: via georef.asset_meter → algún campo de suministro
    try:
        cur.execute(
            """
            SELECT column_name
            FROM all_tab_columns
            WHERE owner = 'GEOREF' AND table_name = 'ASSET_METER'
            ORDER BY column_id
            """,
        )
        cols = [r[0] for r in cur.fetchall()]
        print(f"\n  Columnas de georef.ASSET_METER: {cols}")
    except Exception as exc:
        print(f"  ERROR listando columnas asset_meter: {exc}")

    print()


# ── Análisis auxiliar: incremental vs acumulado ──────────────────────────────


def _analizar_incremento(rows: list, cols: list) -> None:
    # Busca columna de valor (EAD o valor_leido)
    valor_col = None
    for c in ("ead", "valor_leido", "value3"):
        if c in cols:
            valor_col = c
            break
    if valor_col is None:
        return

    idx = cols.index(valor_col)
    valores = [row[idx] for row in rows if row[idx] is not None]
    if len(valores) < 3:
        return

    diffs = [valores[i + 1] - valores[i] for i in range(len(valores) - 1)]
    positivos = sum(1 for d in diffs if d > 0)
    negativos = sum(1 for d in diffs if d < 0)
    todos_similares = all(abs(d) < 2.0 for d in diffs)  # heurística < 2 kWh/15min

    print(f"\n  Análisis de '{valor_col}':")
    print(f"    Rango de valores: {min(valores):.4f} – {max(valores):.4f}")
    print(f"    Diffs: {[round(d, 4) for d in diffs[:10]]}")
    print(f"    Diffs positivos: {positivos}, negativos: {negativos}")

    if max(valores) > 10_000:
        print("    → PROBABLE ACUMULADO (valores > 10.000, típico de contador corriendo)")
    elif todos_similares and positivos > negativos:
        print("    → PROBABLE INCREMENTAL (valores pequeños y similares, típico de kWh/período)")
    else:
        print("    → INDETERMINADO — revisar manualmente")


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Spike Oracle perfiles georef")
    parser.add_argument("--equipo", default="91013496", help="Número de medidor (sn)")
    parser.add_argument("--dias", type=int, default=2, help="Días hacia atrás a consultar")
    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"  SPIKE: Oracle perfiles georef — equipo={args.equipo}, días={args.dias}")
    print(f"{'=' * 70}\n")

    conn = _conectar()
    try:
        with conn.cursor() as cur:
            verificar_acceso(cur)
            describir_columnas(cur)
            muestra_georef(cur, args.equipo, args.dias)
            muestra_vista_perfil(cur, args.equipo, args.dias)
            verificar_granularidad(cur, args.equipo)
            verificar_link_srv(cur, args.equipo)
    finally:
        conn.rollback()
        conn.close()

    print("=" * 70)
    print("  SPIKE COMPLETADO — Ver output arriba para conclusiones")
    print("=" * 70)


if __name__ == "__main__":
    main()
