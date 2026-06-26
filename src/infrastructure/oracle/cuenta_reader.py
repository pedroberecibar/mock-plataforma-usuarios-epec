"""Lee la metadata de cuenta de un suministro desde Oracle.

Fuente: GEOREF.VM_INTELIGENTES (identidad, dirección, tarifa legible, medidor)
con LEFT JOIN a GEOREF.VM_SUMINISTROS para la fase del medidor. Read-only.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import os
from collections.abc import Sequence
from typing import Any

import oracledb

from domain.cuenta import CuentaSuministroRaw
from domain.ports.cuenta_reader import CuentaReader
from infrastructure.oracle.medicion_reader import _init_oracle_client

_QUERY_CUENTA = """
SELECT i.RAZON_SOCIAL, i.TIPO_DOCUMENTO, i.NRO_DOCUMENTO, i.CUIT,
       i.CALLE, i.ALTURA, i.PISO, i.DEPTO, i.TORRE, i.BARRIO, i.LOCALIDAD, i.CP,
       i.DATOS_ADICIONALES_DOMICILIO, i.ESTADO_SERVICIO,
       i.TELEMEDIBLE, i.MEDIDOR, i.TELEMEDIBLE_DESDE,
       i.CODIGO_TARIFA, i.TARIFA, i.GRUPO_TARIFARIO, i.CLASE, i.DESCRIPCION_CLASE,
       i.TENSION, s.MEDIDOR_FASES
FROM   GEOREF.VM_INTELIGENTES i
LEFT JOIN GEOREF.VM_SUMINISTROS s ON s.SUMINISTRO = i.SUMINISTRO
WHERE  i.SUMINISTRO = :suministro_id
FETCH FIRST 1 ROW ONLY
"""


def _str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _date(value: object) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return None


def _row_to_raw(row: Sequence[Any]) -> CuentaSuministroRaw:
    return CuentaSuministroRaw(
        razon_social=_str(row[0]),
        tipo_documento=_str(row[1]),
        nro_documento=_str(row[2]),
        cuit=_str(row[3]),
        calle=_str(row[4]),
        altura=_str(row[5]),
        piso=_str(row[6]),
        depto=_str(row[7]),
        torre=_str(row[8]),
        barrio=_str(row[9]),
        localidad=_str(row[10]),
        cp=_str(row[11]),
        datos_adicionales=_str(row[12]),
        estado_servicio=_str(row[13]),
        telemedible=_str(row[14]),
        medidor=_str(row[15]),
        telemedible_desde=_date(row[16]),
        codigo_tarifa=_str(row[17]),
        tarifa=_str(row[18]),
        grupo_tarifario=_str(row[19]),
        clase=_str(row[20]),
        clase_descripcion=_str(row[21]),
        tension=_str(row[22]),
        medidor_fases=_str(row[23]),
    )


class OracleCuentaReader(CuentaReader):
    def __init__(self) -> None:
        _init_oracle_client()
        self._dsn = oracledb.makedsn(
            host=os.environ["OR_HOST"],
            port=int(os.environ.get("OR_PORT", "1521")),
            service_name=os.environ["OR_SERVICE_NAME"],
        )
        self._user = os.environ["OR_USER"]
        self._password = os.environ["OR_PASS"]

    def _fetch_sync(self, suministro_id: str) -> CuentaSuministroRaw | None:
        oracle_id = int(suministro_id.removeprefix("SRV-"))
        with oracledb.connect(user=self._user, password=self._password, dsn=self._dsn) as conn:
            conn.autocommit = False
            conn.call_timeout = 15_000
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
            with conn.cursor() as cur:
                cur.execute(_QUERY_CUENTA, {"suministro_id": oracle_id})
                row = cur.fetchone()
            conn.rollback()
        if row is None:
            return None
        return _row_to_raw(row)

    async def leer_cuenta(self, suministro_id: str) -> CuentaSuministroRaw | None:
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._fetch_sync, suministro_id),
                timeout=20.0,
            )
        except Exception:
            return None
