import collections
import os
from datetime import date
from typing import Any

import oracledb

from domain.lecturas import LecturaTelemedida
from domain.ports.medicion_source_reader import MedicionSourceReader

_THIN_CLIENT_INITIALIZED = False

# JOIN con XXSIGEC.EQUIPOS resuelve el mapeo medidor (STE_NUMERO) -> suministro (SRV_CODIGO).
# Lecturas sin entrada en EQUIPOS son descartadas por el INNER JOIN (medidor no registrado).
_QUERY_RANGO = """
SELECT e.SRV_CODIGO AS srv_codigo,
       l.med_numero_equipo, l.cdr_codigo,
       TRUNC(l.lec_fecha_lectura) AS fecha,
       l.lec_valor_leido
FROM xxsigec.XXCO_LECTURAS_TELEMEDIDAS l
JOIN xxsigec.EQUIPOS e ON e.STE_NUMERO = l.med_numero_equipo
WHERE l.cdr_codigo = 'E'
  AND l.lec_valor_leido IS NOT NULL
  AND l.lec_fecha_lectura >= :desde
  AND l.lec_fecha_lectura <= :hasta
UNION ALL
SELECT e.SRV_CODIGO AS srv_codigo,
       l.med_numero_equipo, l.cdr_codigo,
       TRUNC(l.lec_fecha_lectura) AS fecha,
       l.lec_valor_leido
FROM xxsigec.XXCO_LECTURAS_TELEMEDIDAS_H l
JOIN xxsigec.EQUIPOS e ON e.STE_NUMERO = l.med_numero_equipo
WHERE l.cdr_codigo = 'E'
  AND l.lec_valor_leido IS NOT NULL
  AND l.lec_fecha_lectura >= :desde
  AND l.lec_fecha_lectura <= :hasta
"""

_QUERY_ANCLAS = """
SELECT srv_codigo, med_numero_equipo, cdr_codigo, fecha, lec_valor_leido
FROM (
    SELECT e.SRV_CODIGO AS srv_codigo,
           l.med_numero_equipo, l.cdr_codigo,
           TRUNC(l.lec_fecha_lectura) AS fecha,
           l.lec_valor_leido,
           ROW_NUMBER() OVER (
               PARTITION BY l.med_numero_equipo
               ORDER BY l.lec_fecha_lectura DESC
           ) AS rn
    FROM (
        SELECT med_numero_equipo, cdr_codigo, lec_fecha_lectura, lec_valor_leido
        FROM xxsigec.XXCO_LECTURAS_TELEMEDIDAS
        WHERE cdr_codigo = 'E'
          AND lec_valor_leido IS NOT NULL
          AND lec_fecha_lectura < :desde
        UNION ALL
        SELECT med_numero_equipo, cdr_codigo, lec_fecha_lectura, lec_valor_leido
        FROM xxsigec.XXCO_LECTURAS_TELEMEDIDAS_H
        WHERE cdr_codigo = 'E'
          AND lec_valor_leido IS NOT NULL
          AND lec_fecha_lectura < :desde
    ) l
    JOIN xxsigec.EQUIPOS e ON e.STE_NUMERO = l.med_numero_equipo
)
WHERE rn = 1
"""


def _init_oracle_client() -> None:
    global _THIN_CLIENT_INITIALIZED
    if _THIN_CLIENT_INITIALIZED:
        return
    lib_dir = os.environ.get("OR_INSTANT_CLIENT")
    if lib_dir:
        try:
            oracledb.init_oracle_client(lib_dir=lib_dir)
        except oracledb.ProgrammingError as exc:
            if "already" not in str(exc).lower():
                raise
    _THIN_CLIENT_INITIALIZED = True


def _normalizar_valor(val: object) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return None


def _set_rowfactory(cursor: Any) -> None:
    """Convierte las filas del cursor de tuplas a namedtuples con acceso por atributo."""
    col_names = [d[0].lower() for d in cursor.description]
    cursor.rowfactory = collections.namedtuple("OracleRow", col_names)  # type: ignore[misc]


def _rows_a_lecturas(cursor: Any) -> list[LecturaTelemedida]:
    resultado: list[LecturaTelemedida] = []
    for row in cursor.fetchall():
        kwh = _normalizar_valor(row.lec_valor_leido)
        if kwh is None:
            continue
        resultado.append(
            LecturaTelemedida(
                equipo=str(row.med_numero_equipo),
                srv_codigo=str(row.srv_codigo),
                cdr_codigo=row.cdr_codigo,
                fecha=row.fecha,
                valor_kwh=kwh,
            )
        )
    return resultado


class OracleMedicionReader(MedicionSourceReader):
    """Adapter Oracle para MedicionSourceReader.

    Usa python-oracledb en modo thin por defecto; activa modo thick si
    OR_INSTANT_CLIENT esta definido en el entorno.
    Fuerza transaccion de solo lectura para no afectar SIGEC.
    """

    def __init__(self) -> None:
        _init_oracle_client()
        self._dsn = oracledb.makedsn(
            host=os.environ["OR_HOST"],
            port=int(os.environ.get("OR_PORT", "1521")),
            service_name=os.environ["OR_SERVICE_NAME"],
        )
        self._user = os.environ["OR_USER"]
        self._password = os.environ["OR_PASS"]

    async def leer_lecturas(self, desde: date, hasta: date) -> list[LecturaTelemedida]:
        with oracledb.connect(user=self._user, password=self._password, dsn=self._dsn) as conn:
            conn.autocommit = False
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")

            with conn.cursor() as cur:
                cur.execute(_QUERY_RANGO, {"desde": desde, "hasta": hasta})
                _set_rowfactory(cur)
                en_rango = _rows_a_lecturas(cur)

            with conn.cursor() as cur:
                cur.execute(_QUERY_ANCLAS, {"desde": desde})
                _set_rowfactory(cur)
                anclas = _rows_a_lecturas(cur)

            conn.rollback()

        return en_rango + anclas
