"""Resuelve cliente/contrato de un suministro desde Oracle GEOREF.VW_INTELIGENTES.

`clienteId` = columna CLIENTE. `contratoId` = suministro + contrato (2 díg.) rellenado
a 10 díg. con ceros a la izquierda. Ver `docs/epec-factura-api-referencia.md`. Read-only.
"""

from __future__ import annotations

import asyncio
import os

import oracledb

from domain.ports.factura_identificadores import (
    FacturaIdentificadores,
    FacturaIdentificadoresReader,
    construir_contrato_id,
)
from infrastructure.oracle.medicion_reader import _init_oracle_client

_QUERY = """
SELECT CLIENTE, SUMINISTRO, CONTRATO
FROM   GEOREF.VW_INTELIGENTES
WHERE  SUMINISTRO = :suministro_id
FETCH FIRST 1 ROW ONLY
"""


class OracleFacturaIdentificadoresReader(FacturaIdentificadoresReader):
    def __init__(self) -> None:
        _init_oracle_client()
        self._dsn = oracledb.makedsn(
            host=os.environ["OR_HOST"],
            port=int(os.environ.get("OR_PORT", "1521")),
            service_name=os.environ["OR_SERVICE_NAME"],
        )
        self._user = os.environ["OR_USER"]
        self._password = os.environ["OR_PASS"]

    def _fetch_sync(self, suministro_id: str) -> FacturaIdentificadores | None:
        oracle_id = int(suministro_id.removeprefix("SRV-"))
        with oracledb.connect(user=self._user, password=self._password, dsn=self._dsn) as conn:
            conn.autocommit = False
            conn.call_timeout = 15_000
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
            with conn.cursor() as cur:
                cur.execute(_QUERY, {"suministro_id": oracle_id})
                row = cur.fetchone()
            conn.rollback()
        if row is None or row[0] is None or row[2] is None:
            return None
        cliente, suministro, contrato = row
        return FacturaIdentificadores(
            cliente_id=str(int(cliente)),
            contrato_id=construir_contrato_id(int(suministro), int(contrato)),
        )

    async def leer(self, suministro_id: str) -> FacturaIdentificadores | None:
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._fetch_sync, suministro_id),
                timeout=20.0,
            )
        except Exception:
            return None
