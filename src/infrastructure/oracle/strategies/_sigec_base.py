"""Lógica compartida para estrategias de ingesta basadas en XXCO_LECTURAS_TELEMEDIDAS."""

from __future__ import annotations

import asyncio
import collections
import os
from datetime import date
from typing import Any

import oracledb

from domain.lecturas import LecturaTelemedida
from domain.perfiles import soporta_perfiles
from domain.ports.suministro_ingestion_strategy import SuministroIngestionStrategy
from infrastructure.oracle.medicion_reader import _init_oracle_client

# Filtra por medidor exacto (un suministro a la vez, distinto al bulk reader).
_QUERY_MEDIDOR = """
SELECT MAX(e.SRV_CODIGO) AS srv_codigo,
       l.med_numero_equipo, l.cdr_codigo,
       TRUNC(l.lec_fecha_lectura) AS fecha,
       MAX(l.lec_valor_leido) KEEP (DENSE_RANK LAST ORDER BY l.lec_fecha_lectura)
           AS lec_valor_leido
FROM xxsigec.XXCO_LECTURAS_TELEMEDIDAS l
JOIN xxsigec.EQUIPOS e ON e.STE_NUMERO = l.med_numero_equipo
WHERE l.cdr_codigo = 'E'
  AND l.lec_valor_leido IS NOT NULL
  AND l.lec_fecha_lectura >= :desde
  AND l.lec_fecha_lectura <= :hasta
  AND l.med_numero_equipo = :medidor
GROUP BY l.med_numero_equipo, l.cdr_codigo, TRUNC(l.lec_fecha_lectura)
UNION ALL
SELECT MAX(e.SRV_CODIGO) AS srv_codigo,
       l.med_numero_equipo, l.cdr_codigo,
       TRUNC(l.lec_fecha_lectura) AS fecha,
       MAX(l.lec_valor_leido) KEEP (DENSE_RANK LAST ORDER BY l.lec_fecha_lectura)
           AS lec_valor_leido
FROM xxsigec.XXCO_LECTURAS_TELEMEDIDAS_H l
JOIN xxsigec.EQUIPOS e ON e.STE_NUMERO = l.med_numero_equipo
WHERE l.cdr_codigo = 'E'
  AND l.lec_valor_leido IS NOT NULL
  AND l.lec_fecha_lectura >= :desde
  AND l.lec_fecha_lectura <= :hasta
  AND l.med_numero_equipo = :medidor
GROUP BY l.med_numero_equipo, l.cdr_codigo, TRUNC(l.lec_fecha_lectura)
"""


def _set_rowfactory(cursor: Any) -> None:
    col_names = [d[0].lower() for d in cursor.description]
    cursor.rowfactory = collections.namedtuple("OracleRow", col_names)  # type: ignore[misc]


def _normalizar_valor(val: object) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return None


class SigecBaseStrategy(SuministroIngestionStrategy):
    """Base para estrategias de ingesta que leen de XXCO_LECTURAS_TELEMEDIDAS.

    Subclases sólo difieren en `nombre` (CLOU, NANSEN, CHUPETE).
    Cuando AMI esté disponible, cada subclase puede sobreescribir `leer_lecturas`.
    """

    # La capacidad de perfiles se deriva del tipo de medidor (nombre) vía la regla de
    # dominio única (ADR-003): CLOU=True, NANSEN/CHUPETE=False. Sin duplicar el criterio.
    @property
    def soporta_perfiles(self) -> bool:
        return soporta_perfiles(self.nombre)

    def __init__(self) -> None:
        _init_oracle_client()
        self._dsn = oracledb.makedsn(
            host=os.environ["OR_HOST"],
            port=int(os.environ.get("OR_PORT", "1521")),
            service_name=os.environ["OR_SERVICE_NAME"],
        )
        self._user = os.environ["OR_USER"]
        self._password = os.environ["OR_PASS"]

    def _fetch_sync(
        self, medidor: str, srv_codigo: str, desde: date, hasta: date
    ) -> list[LecturaTelemedida]:
        params: dict[str, object] = {"desde": desde, "hasta": hasta, "medidor": medidor}
        with oracledb.connect(user=self._user, password=self._password, dsn=self._dsn) as conn:
            conn.autocommit = False
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
            with conn.cursor() as cur:
                conn.call_timeout = 30_000
                cur.arraysize = 10_000
                cur.execute(_QUERY_MEDIDOR, params)
                _set_rowfactory(cur)
                resultado: list[LecturaTelemedida] = []
                for row in cur.fetchall():
                    kwh = _normalizar_valor(row.lec_valor_leido)
                    if kwh is not None:
                        resultado.append(
                            LecturaTelemedida(
                                equipo=str(row.med_numero_equipo),
                                srv_codigo=srv_codigo,  # canonical ID, not Oracle raw SRV_CODIGO
                                cdr_codigo=row.cdr_codigo,
                                fecha=row.fecha,
                                valor_kwh=kwh,
                            )
                        )
            conn.rollback()
        return resultado

    async def leer_lecturas(
        self, medidor: str, srv_codigo: str, desde: date, hasta: date
    ) -> list[LecturaTelemedida]:
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._fetch_sync, medidor, srv_codigo, desde, hasta),
                timeout=35.0,
            )
        except Exception:
            return []
