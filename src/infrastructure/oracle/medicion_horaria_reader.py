"""Adapter Oracle para MedicionHorariaSourceReader.

Lee lecturas acumuladas de XXCO_LECTURAS_TELEMEDIDAS_H agrupadas por hora
(TRUNC('HH')), del mismo modo que OracleMedicionReader lo hace por día
(TRUNC sin argumento). El campo `fecha_hora` es un datetime de Python —
extraemos .date() y .hour para poblar LecturaHoraria.

Conexión en modo thin por defecto; modo thick si OR_INSTANT_CLIENT está definido.
Fuerza SET TRANSACTION READ ONLY para no afectar SIGEC.
"""

import os
from datetime import date, datetime
from typing import Any

import oracledb

from domain.lecturas_horarias import LecturaHoraria
from domain.ports.medicion_horaria_source_reader import MedicionHorariaSourceReader
from infrastructure.oracle.medicion_reader import (
    _init_oracle_client,
    _normalizar_valor,
    _set_rowfactory,
)

# KEEP LAST dentro de cada ventana horaria: queremos el valor acumulado más
# reciente de cada hora (el contador sigue subiendo intrahora).
_QUERY_HORARIA_TMPL = """
SELECT MAX(e.SRV_CODIGO) AS srv_codigo,
       l.med_numero_equipo,
       l.cdr_codigo,
       TRUNC(l.lec_fecha_lectura, 'HH') AS fecha_hora,
       MAX(l.lec_valor_leido) KEEP (DENSE_RANK LAST ORDER BY l.lec_fecha_lectura)
           AS lec_valor_leido
  FROM xxsigec.XXCO_LECTURAS_TELEMEDIDAS_H l
  JOIN xxsigec.EQUIPOS e ON e.STE_NUMERO = l.med_numero_equipo
 WHERE l.cdr_codigo = 'E'
   AND l.lec_valor_leido IS NOT NULL
   AND l.lec_fecha_lectura >= :desde
   AND l.lec_fecha_lectura <= :hasta
   {equipo_filter}
 GROUP BY l.med_numero_equipo, l.cdr_codigo, TRUNC(l.lec_fecha_lectura, 'HH')
 ORDER BY l.med_numero_equipo, TRUNC(l.lec_fecha_lectura, 'HH')
"""


def _rows_a_lecturas_horarias(cursor: Any) -> list[LecturaHoraria]:
    resultado: list[LecturaHoraria] = []
    for row in cursor.fetchall():
        kwh = _normalizar_valor(row.lec_valor_leido)
        if kwh is None:
            continue
        # fecha_hora es un datetime (Oracle DATE con componente de tiempo)
        fh: datetime = row.fecha_hora
        resultado.append(
            LecturaHoraria(
                equipo=str(row.med_numero_equipo),
                srv_codigo=str(row.srv_codigo),
                cdr_codigo=row.cdr_codigo,
                fecha=fh.date() if isinstance(fh, datetime) else date(fh.year, fh.month, fh.day),
                hora=fh.hour if isinstance(fh, datetime) else 0,
                valor_kwh=kwh,
            )
        )
    return resultado


class OracleMedicionHorariaReader(MedicionHorariaSourceReader):
    def __init__(self) -> None:
        _init_oracle_client()
        self._dsn = oracledb.makedsn(
            host=os.environ["OR_HOST"],
            port=int(os.environ.get("OR_PORT", "1521")),
            service_name=os.environ["OR_SERVICE_NAME"],
        )
        self._user = os.environ["OR_USER"]
        self._password = os.environ["OR_PASS"]

    async def leer_lecturas_horarias(
        self,
        desde: date,
        hasta: date,
        equipos: list[str] | None = None,
    ) -> list[LecturaHoraria]:
        params: dict[str, object] = {"desde": desde, "hasta": hasta}
        if equipos:
            placeholders = ", ".join(f":eq{i}" for i in range(len(equipos)))
            equipo_filter = f"AND l.med_numero_equipo IN ({placeholders})"
            params.update({f"eq{i}": eq for i, eq in enumerate(equipos)})
        else:
            equipo_filter = ""

        query = _QUERY_HORARIA_TMPL.format(equipo_filter=equipo_filter)

        with oracledb.connect(user=self._user, password=self._password, dsn=self._dsn) as conn:
            conn.autocommit = False
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")

            with conn.cursor() as cur:
                cur.arraysize = 10_000
                cur.execute(query, params)
                _set_rowfactory(cur)
                lecturas = _rows_a_lecturas_horarias(cur)

            conn.rollback()

        return lecturas
