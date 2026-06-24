"""Adapter Oracle para VecinosRepository.

Obtiene vecinos por subestación usando GEOREF.VW_INTELIGENTES.SUBESTACION.
Dada una subestación, retorna todos los suministros que comparten esa subestación
excluyendo el suministro de referencia.

Mantiene los helpers del scheduler (resolver_srv_de_equipos, get_equipos_activos_de_srvs)
que operan sobre XXSIGEC.EQUIPOS/SERVICIOS y no cambian.
"""

import asyncio
import collections
import contextlib
import os
from typing import Any

import oracledb

from domain.ports.vecinos_repository import VecinosRepository

_THIN_CLIENT_INITIALIZED = False

_QUERY_VECINOS_SUBESTACION = """
SELECT TO_CHAR(SUMINISTRO) AS SUMINISTRO
FROM   GEOREF.VW_INTELIGENTES
WHERE  SUBESTACION = (
           SELECT SUBESTACION
           FROM   GEOREF.VW_INTELIGENTES
           WHERE  SUMINISTRO = :suministro_id
           FETCH FIRST 1 ROW ONLY
       )
  AND  SUMINISTRO != :suministro_id
"""

# Dado un conjunto de med_numero_equipo, devuelve su SRV_CODIGO
_QUERY_SRV_DE_EQUIPOS = """
SELECT STE_NUMERO, MAX(SRV_CODIGO) AS SRV_CODIGO
FROM   XXSIGEC.EQUIPOS
WHERE  STE_NUMERO IN ({placeholders})
GROUP  BY STE_NUMERO
"""

# Dado un conjunto de SRV_CODIGO (como ints), devuelve el medidor activo de cada uno.
# Usa VW_INTELIGENTES para cubrir tanto NANSEN ('SN') como CLOU y otros tipos.
# SUMINISTRO es NUMBER — se bindea como int para aprovechar índice (no TO_CHAR).
_QUERY_EQUIPOS_ACTIVOS = """
SELECT MEDIDOR AS STE_NUMERO
FROM   GEOREF.VW_INTELIGENTES
WHERE  SUMINISTRO IN ({placeholders})
  AND  MEDIDOR IS NOT NULL
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


def _set_rowfactory(cursor: Any) -> None:
    col_names = [d[0].lower() for d in cursor.description]
    cursor.rowfactory = collections.namedtuple("OracleRow", col_names)  # type: ignore[misc]


class OracleVecinosRepository(VecinosRepository):
    def __init__(self) -> None:
        _init_oracle_client()
        self._dsn = oracledb.makedsn(
            host=os.environ["OR_HOST"],
            port=int(os.environ.get("OR_PORT", "1521")),
            service_name=os.environ["OR_SERVICE_NAME"],
        )
        self._user = os.environ["OR_USER"]
        self._password = os.environ["OR_PASS"]

    def _connect(self) -> oracledb.Connection:
        conn = oracledb.connect(user=self._user, password=self._password, dsn=self._dsn)
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
        return conn

    # ------------------------------------------------------------------
    # Vecinos por subestación
    # ------------------------------------------------------------------

    def _fetch_vecinos_sync(self, suministro_id: str) -> list[str]:
        try:
            oracle_id = int(suministro_id.removeprefix("SRV-"))
        except ValueError:
            return []
        try:
            with self._connect() as conn:
                conn.call_timeout = 20_000
                with conn.cursor() as cur:
                    cur.arraysize = 10_000
                    cur.execute(_QUERY_VECINOS_SUBESTACION, {"suministro_id": oracle_id})
                    rows = cur.fetchall()
                conn.rollback()
        except Exception:
            return []
        return [str(r[0]) for r in rows]

    async def get_vecinos(self, suministro_id: str) -> list[str]:
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._fetch_vecinos_sync, suministro_id),
                timeout=25.0,
            )
        except (TimeoutError, Exception):
            return []

    # ------------------------------------------------------------------
    # Helpers para el scheduler: resolución equipo ↔ suministro
    # ------------------------------------------------------------------

    def _fetch_srv_de_equipos_sync(self, equipos: list[str]) -> dict[str, str]:
        placeholders = ", ".join(f":e{i}" for i in range(len(equipos)))
        params = {f"e{i}": eq for i, eq in enumerate(equipos)}
        try:
            with self._connect() as conn:
                conn.call_timeout = 15_000
                with conn.cursor() as cur:
                    cur.execute(_QUERY_SRV_DE_EQUIPOS.format(placeholders=placeholders), params)
                    rows = cur.fetchall()
                conn.rollback()
            return {str(r[0]): str(r[1]) for r in rows}
        except Exception:
            return {}

    async def resolver_srv_de_equipos(self, equipos: list[str]) -> dict[str, str]:
        """Dado {med_numero_equipo}, devuelve {med_numero_equipo: SRV_CODIGO}."""
        if not equipos:
            return {}
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._fetch_srv_de_equipos_sync, equipos),
                timeout=20.0,
            )
        except (TimeoutError, Exception):
            return {}

    def _fetch_equipos_activos_sync(self, srv_codigos: list[str]) -> list[str]:
        # Convierte a int para bindear sin TO_CHAR — preserva el índice numérico de SUMINISTRO
        ids_int = []
        for s in srv_codigos:
            with contextlib.suppress(ValueError):
                ids_int.append(int(s))
        if not ids_int:
            return []
        placeholders = ", ".join(f":s{i}" for i in range(len(ids_int)))
        params = {f"s{i}": v for i, v in enumerate(ids_int)}
        try:
            with self._connect() as conn:
                conn.call_timeout = 30_000
                with conn.cursor() as cur:
                    cur.arraysize = 10_000
                    cur.execute(_QUERY_EQUIPOS_ACTIVOS.format(placeholders=placeholders), params)
                    rows = cur.fetchall()
                conn.rollback()
            return [str(r[0]) for r in rows]
        except Exception:
            return []

    async def get_equipos_activos_de_srvs(self, srv_codigos: list[str]) -> list[str]:
        """Dado SRV_CODIGOs vecinos, devuelve sus med_numero_equipo activos y telemedibles."""
        if not srv_codigos:
            return []
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._fetch_equipos_activos_sync, srv_codigos),
                timeout=60.0,
            )
        except (TimeoutError, Exception):
            return []
