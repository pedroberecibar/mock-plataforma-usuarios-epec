"""Lee metadata de un suministro desde GEOREF.VW_INTELIGENTES."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass

import oracledb

from infrastructure.oracle.medicion_reader import _init_oracle_client

_QUERY_META = """
SELECT MEDIDOR, TELEMEDIBLE, DC_LATITUD, DC_LONGITUD, SUBESTACION, CODIGO_TARIFA
FROM   GEOREF.VW_INTELIGENTES
WHERE  SUMINISTRO = :suministro_id
FETCH FIRST 1 ROW ONLY
"""


@dataclass(frozen=True)
class SuministroMeta:
    medidor: str | None
    telemedible: str | None
    lat: float | None
    lon: float | None
    subestacion: str | None
    codigo_tarifa: str | None


class OracleSuministroMetaReader:
    def __init__(self) -> None:
        _init_oracle_client()
        self._dsn = oracledb.makedsn(
            host=os.environ["OR_HOST"],
            port=int(os.environ.get("OR_PORT", "1521")),
            service_name=os.environ["OR_SERVICE_NAME"],
        )
        self._user = os.environ["OR_USER"]
        self._password = os.environ["OR_PASS"]

    def _fetch_sync(self, suministro_id: str) -> SuministroMeta | None:
        oracle_id = int(suministro_id.removeprefix("SRV-"))
        with oracledb.connect(user=self._user, password=self._password, dsn=self._dsn) as conn:
            conn.autocommit = False
            conn.call_timeout = 15_000
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
            with conn.cursor() as cur:
                cur.execute(_QUERY_META, {"suministro_id": oracle_id})
                row = cur.fetchone()
            conn.rollback()
        if row is None:
            return None
        medidor, telemedible, lat, lon, subestacion, codigo_tarifa = row

        def _to_float(v: object) -> float | None:
            try:
                return float(str(v)) if v is not None else None
            except (TypeError, ValueError):
                return None

        return SuministroMeta(
            medidor=str(medidor) if medidor is not None else None,
            telemedible=str(telemedible) if telemedible is not None else None,
            lat=_to_float(lat),
            lon=_to_float(lon),
            subestacion=str(subestacion) if subestacion is not None else None,
            codigo_tarifa=str(codigo_tarifa) if codigo_tarifa is not None else None,
        )

    async def leer_meta(self, suministro_id: str) -> SuministroMeta | None:
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._fetch_sync, suministro_id),
                timeout=20.0,
            )
        except Exception:
            return None
