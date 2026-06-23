"""Adapter Oracle para VecinosRepository.

Busca vecinos por radio geográfico usando SRV_GPS_LATITUD / SRV_GPS_LONGITUD
de XXSIGEC.SERVICIOS. El bounding-box cuadrado se calcula en grados (aprox. delta
grados por cada radio_metros metros); luego se aplica filtro haversine exacto en
Python para descartar las esquinas del cuadrado.

El enfoque AGF_CODIGO previo fue reemplazado porque su granularidad es a nivel
de manzana/área y no garantiza proximidad real de 150 m.
"""

import asyncio
import collections
import math
import os
from typing import Any

import oracledb

from domain.ports.vecinos_repository import VecinosRepository

_THIN_CLIENT_INITIALIZED = False

# Bounding box + ref coords en una sola query (sin round-trip extra para ref lat/lon)
_QUERY_VECINOS = """
SELECT s2.SRV_CODIGO,
       s2.SRV_GPS_LATITUD,
       s2.SRV_GPS_LONGITUD,
       s1.SRV_GPS_LATITUD  AS ref_lat,
       s1.SRV_GPS_LONGITUD AS ref_lon
FROM   XXSIGEC.SERVICIOS s1
JOIN   XXSIGEC.SERVICIOS s2
       ON  s2.SRV_GPS_LATITUD  BETWEEN s1.SRV_GPS_LATITUD  - :delta
                                    AND s1.SRV_GPS_LATITUD  + :delta
       AND s2.SRV_GPS_LONGITUD BETWEEN s1.SRV_GPS_LONGITUD - :delta
                                    AND s1.SRV_GPS_LONGITUD + :delta
WHERE  s1.SRV_CODIGO       = :suministro_id
  AND  s2.SRV_CODIGO      != :suministro_id
  AND  s2.SRV_GPS_LATITUD  IS NOT NULL
  AND  s2.SRV_GPS_LONGITUD IS NOT NULL
"""

# Dado un conjunto de med_numero_equipo, devuelve su SRV_CODIGO
_QUERY_SRV_DE_EQUIPOS = """
SELECT STE_NUMERO, MAX(SRV_CODIGO) AS SRV_CODIGO
FROM   XXSIGEC.EQUIPOS
WHERE  STE_NUMERO IN ({placeholders})
GROUP  BY STE_NUMERO
"""

# Dado un conjunto de SRV_CODIGO, devuelve el equipo activo de cada uno
# filtrando por telemedición habilitada para evitar ingestas vacías
_QUERY_EQUIPOS_ACTIVOS = """
SELECT DISTINCT e.STE_NUMERO
FROM   XXSIGEC.EQUIPOS   e
JOIN   XXSIGEC.SERVICIOS s ON s.SRV_CODIGO = e.SRV_CODIGO
WHERE  e.SRV_CODIGO       IN ({placeholders})
  AND  e.EQP_FECHA_RETIRO IS NULL
  AND  s.SRV_TELEMEDIBLE   = 'SN'
"""


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return r * 2 * math.asin(math.sqrt(a))


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
    # Vecinos por radio geográfico
    # ------------------------------------------------------------------

    def _fetch_vecinos_sync(
        self, suministro_id: str, radio_metros: float
    ) -> list[tuple[str, float, float]]:
        delta = radio_metros / 111_000.0
        try:
            with self._connect() as conn:
                conn.call_timeout = 15_000
                with conn.cursor() as cur:
                    cur.arraysize = 10_000
                    cur.execute(
                        _QUERY_VECINOS,
                        {"suministro_id": suministro_id, "delta": delta},
                    )
                    _set_rowfactory(cur)
                    rows = cur.fetchall()
                conn.rollback()
        except Exception:
            return []

        if not rows:
            return []

        ref_lat = float(rows[0].ref_lat)
        ref_lon = float(rows[0].ref_lon)

        return [
            (str(r.srv_codigo), float(r.srv_gps_latitud), float(r.srv_gps_longitud))
            for r in rows
            if _haversine(ref_lat, ref_lon, float(r.srv_gps_latitud), float(r.srv_gps_longitud))
            <= radio_metros
        ]

    async def get_vecinos_con_coordenadas(
        self, suministro_id: str, radio_metros: float
    ) -> list[tuple[str, float, float]]:
        """Devuelve (SRV_CODIGO, lat, lon) para vecinos dentro del radio exacto."""
        loop = asyncio.get_running_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._fetch_vecinos_sync, suministro_id, radio_metros),
                timeout=20.0,
            )
        except (TimeoutError, Exception):
            return []

    async def get_vecinos(self, suministro_id: str, radio_metros: float) -> list[str]:
        entries = await self.get_vecinos_con_coordenadas(suministro_id, radio_metros)
        return [e[0] for e in entries]

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
        placeholders = ", ".join(f":s{i}" for i in range(len(srv_codigos)))
        params = {f"s{i}": s for i, s in enumerate(srv_codigos)}
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
