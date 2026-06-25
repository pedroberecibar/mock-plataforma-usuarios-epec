# -*- coding: utf-8 -*-
"""Diagnostico de integracion para suministro 2817670 (Natalia Palacios).

Verifica el pipeline completo (solo lectura):
  1. Metadata desde GEOREF.VM_INTELIGENTES
  2. Lecturas SIGEC (XXCO_LECTURAS_TELEMEDIDAS) para el medidor encontrado
  3. Lecturas AMI (SHENYU1) via QUERY_ASSET_METER
  4. Vecinos via subestacion
  5. Nombre desde XXSIGEC.PERSONAS

NO MODIFICA NADA. Solo SELECT.

Uso:
    uv run python scripts/spike_test_perfil_2817670.py
"""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from pathlib import Path

# bootstrap
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

SUMINISTRO = "2817670"
SEP = "-" * 72
DESDE = (date.today() - timedelta(days=90)).strftime("%Y-%m-%d")
HASTA = date.today().strftime("%Y-%m-%d")


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


def titulo(texto: str) -> None:
    print(f"\n{SEP}")
    print(f"  {texto}")
    print(SEP)


def ok(msg: str) -> None:
    print(f"  [OK]   {msg}")


def warn(msg: str) -> None:
    print(f"  [WARN] {msg}")


def err(msg: str) -> None:
    print(f"  [ERR]  {msg}")


# Query SIGEC reutilizando la misma logica que SigecBaseStrategy
_SIGEC_LECTURAS_SQL = """
SELECT TRUNC(l.lec_fecha_lectura) AS fecha,
       MAX(l.lec_valor_leido) KEEP (DENSE_RANK LAST ORDER BY l.lec_fecha_lectura)
           AS kwh
FROM xxsigec.XXCO_LECTURAS_TELEMEDIDAS l
WHERE l.cdr_codigo = 'E'
  AND l.lec_valor_leido IS NOT NULL
  AND l.lec_fecha_lectura >= TO_DATE(:desde, 'YYYY-MM-DD')
  AND l.lec_fecha_lectura <= TO_DATE(:hasta, 'YYYY-MM-DD')
  AND l.med_numero_equipo = :med
GROUP BY TRUNC(l.lec_fecha_lectura)
UNION ALL
SELECT TRUNC(l.lec_fecha_lectura) AS fecha,
       MAX(l.lec_valor_leido) KEEP (DENSE_RANK LAST ORDER BY l.lec_fecha_lectura)
           AS kwh
FROM xxsigec.XXCO_LECTURAS_TELEMEDIDAS_H l
WHERE l.cdr_codigo = 'E'
  AND l.lec_valor_leido IS NOT NULL
  AND l.lec_fecha_lectura >= TO_DATE(:desde, 'YYYY-MM-DD')
  AND l.lec_fecha_lectura <= TO_DATE(:hasta, 'YYYY-MM-DD')
  AND l.med_numero_equipo = :med
GROUP BY TRUNC(l.lec_fecha_lectura)
"""


def main() -> None:
    print(f"\n{'=' * 72}")
    print(f"  DIAGNOSTICO PERFIL - Suministro {SUMINISTRO}")
    print(f"  Rango: {DESDE} -> {HASTA}  (ultimos 90 dias)")
    print(f"{'=' * 72}")

    conn = _conectar()
    ok("Conexion Oracle establecida")

    medidor = None
    telemedible = None
    cliente_id = None
    subestacion = None

    try:
        with conn.cursor() as cur:
            # 1. METADATA
            titulo("1. GEOREF.VM_INTELIGENTES - metadata del suministro")
            cur.execute(
                """
                SELECT SUMINISTRO, MEDIDOR, TELEMEDIBLE, DC_LATITUD, DC_LONGITUD,
                       SUBESTACION, CODIGO_TARIFA, CLIENTE
                FROM GEOREF.VM_INTELIGENTES
                WHERE SUMINISTRO = :srv
                """,
                {"srv": SUMINISTRO},
            )
            row = cur.fetchone()
            if row is None:
                err(f"Suministro {SUMINISTRO} NO encontrado en VM_INTELIGENTES")
                return
            cols = [d[0].lower() for d in cur.description]
            meta = dict(zip(cols, row, strict=False))
            ok(f"Encontrado: {meta}")
            medidor = meta.get("medidor")
            telemedible = meta.get("telemedible")
            cliente_id = meta.get("cliente")
            subestacion = meta.get("subestacion")
            ok(
                f"Medidor: {medidor}  |  Telemedible: {telemedible}  |  Tarifa: {meta.get('codigo_tarifa')}"
            )

            # 2. NOMBRE
            titulo("2. XXSIGEC.PERSONAS - nombre del titular")
            if cliente_id:
                cur.execute(
                    """
                    SELECT PRS_NUMERO, PRS_DOCUMENTO, PRS_RAZON_SOCIAL
                    FROM XXSIGEC.PERSONAS
                    WHERE PRS_NUMERO = :id
                    """,
                    {"id": cliente_id},
                )
                prow = cur.fetchone()
                if prow:
                    ok(f"Titular: {prow[2]}  |  DNI: {prow[1]}")
                else:
                    warn(f"CLIENTE {cliente_id} no encontrado en PERSONAS")
            else:
                warn("Sin CLIENTE en VM_INTELIGENTES")

            # 3. LECTURAS SIGEC
            titulo("3. XXCO_LECTURAS_TELEMEDIDAS (SIGEC) - lecturas del medidor")
            if medidor:
                params = {"med": medidor, "desde": DESDE, "hasta": HASTA}
                cur.execute(
                    f"SELECT COUNT(*), MIN(fecha), MAX(fecha), ROUND(SUM(kwh), 2) FROM ({_SIGEC_LECTURAS_SQL})",
                    params,
                )
                r = cur.fetchone()
                if r and r[0]:
                    ok(f"SIGEC: {r[0]} dias con lectura  |  {r[1]} -> {r[2]}  |  total: {r[3]} kWh")
                    # Ultimas 5
                    cur.execute(
                        f"SELECT fecha, kwh FROM ({_SIGEC_LECTURAS_SQL}) ORDER BY fecha DESC FETCH FIRST 5 ROWS ONLY",
                        params,
                    )
                    print("  Ultimas 5 lecturas SIGEC:")
                    for lrow in cur.fetchall():
                        print(f"    {lrow[0].strftime('%Y-%m-%d')}  ->  {lrow[1]:.2f} kWh")
                else:
                    warn(f"Sin lecturas SIGEC para medidor {medidor} en el rango indicado")
            else:
                warn("Sin medidor - salteando SIGEC")

            # 4. LECTURAS AMI (SHENYU1)
            titulo("4. GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 (AMI CLOU)")
            if medidor:
                cur.execute(
                    "SELECT ID, SN FROM GEOREF.QUERY_ASSET_METER WHERE SN LIKE :pat FETCH FIRST 3 ROWS ONLY",
                    {"pat": f"%{medidor}"},
                )
                qam_rows = cur.fetchall()
                if qam_rows:
                    uuid = qam_rows[0][0]
                    ok(f"QUERY_ASSET_METER: SN={qam_rows[0][1]} -> UUID={uuid}")
                    cur.execute(
                        "SELECT COUNT(*), MIN(TV), MAX(TV) FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 WHERE DEVICE_ID = :uid AND TV >= SYSDATE - 90",
                        {"uid": uuid},
                    )
                    sr = cur.fetchone()
                    if sr and sr[0]:
                        ok(f"SHENYU1: {sr[0]} filas  |  {sr[1]} -> {sr[2]}")
                    else:
                        warn(f"Sin datos en SHENYU1 para UUID {uuid}")
                else:
                    warn(f"Medidor {medidor} no en QUERY_ASSET_METER (esperado para NANSEN)")
                    cur.execute(
                        "SELECT COUNT(*) FROM GEOREF.QUERY_DATA_MD_PROFILE_MINUTELY_SHENYU1 WHERE DEVICE_ID = :med AND TV >= SYSDATE - 90",
                        {"med": medidor},
                    )
                    n_direct = cur.fetchone()[0]
                    if n_direct:
                        ok(f"SHENYU1 directo (DEVICE_ID=medidor): {n_direct} filas")
                    else:
                        warn("SHENYU1 directo: sin datos (NANSEN sin AMI en SHENYU1)")

            # 5. VECINOS
            titulo("5. Vecinos por subestacion")
            if subestacion:
                cur.execute(
                    "SELECT COUNT(*) FROM GEOREF.VM_INTELIGENTES WHERE SUBESTACION = :sub AND SUMINISTRO != :srv",
                    {"sub": subestacion, "srv": SUMINISTRO},
                )
                n_vec = cur.fetchone()[0]
                ok(f"Subestacion {subestacion}: {n_vec} vecinos disponibles")
            else:
                warn("Sin subestacion - no se pueden calcular vecinos")

            # RESUMEN
            titulo("RESUMEN")
            print(f"  Suministro  : {SUMINISTRO}")
            print(f"  Medidor     : {medidor or '---'}")
            print(f"  Telemedible : {telemedible or '---'}")
            print(f"  Subestacion : {subestacion or '---'}")
            print(f"  Tarifa      : {meta.get('codigo_tarifa') or '---'}")
            print(
                f"  SIGEC       : {'disponible (via XXCO_LECTURAS_TELEMEDIDAS)' if medidor else 'sin medidor'}"
            )
            print(
                f"  AMI (SHENYU): {'no aplica - NANSEN usa SIGEC' if telemedible == 'NANSEN' else 'revisar manualmente'}"
            )
            print(f"  Vecinos     : {'disponible' if subestacion else 'sin subestacion'}")
            print()

    finally:
        conn.rollback()
        conn.close()

    print("=" * 72)
    print("  DIAGNOSTICO COMPLETO")
    print("=" * 72)


if __name__ == "__main__":
    main()
