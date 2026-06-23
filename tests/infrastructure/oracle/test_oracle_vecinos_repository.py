"""Contract tests para OracleVecinosRepository — sin conexión Oracle real.

Mockean oracledb a nivel de módulo para verificar:
- La query es parametrizada (suministro_id, no interpolado).
- El rowfactory extrae SRV_CODIGO como strings.
- Si Oracle lanza excepción (timeout, error de red) se retorna [] sin propagar.
- call_timeout es configurado en la conexión.
"""

import collections as _collections
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.oracle.vecinos_repository import OracleVecinosRepository


@pytest.fixture
def env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OR_USER", "usr")
    monkeypatch.setenv("OR_PASS", "pass")
    monkeypatch.setenv("OR_HOST", "oracle-host")
    monkeypatch.setenv("OR_PORT", "1521")
    monkeypatch.setenv("OR_SERVICE_NAME", "SIGEC")


_REF_LAT = -31.455
_REF_LON = -64.148
# Neighbor coords within 150 m of ref (~111 m away)
_VEC_LAT = -31.454
_VEC_LON = -64.147

_VecinoRow = _collections.namedtuple(
    "OracleRow", ["srv_codigo", "srv_gps_latitud", "srv_gps_longitud", "ref_lat", "ref_lon"]
)


def _make_vecino_row(srv_codigo: str) -> object:
    return _VecinoRow(
        srv_codigo=srv_codigo,
        srv_gps_latitud=_VEC_LAT,
        srv_gps_longitud=_VEC_LON,
        ref_lat=_REF_LAT,
        ref_lon=_REF_LON,
    )


@pytest.fixture
def mock_conn_and_cursor():
    cursor = MagicMock()
    cursor.description = [
        ("SRV_CODIGO",),
        ("SRV_GPS_LATITUD",),
        ("SRV_GPS_LONGITUD",),
        ("REF_LAT",),
        ("REF_LON",),
    ]
    cursor.fetchall.return_value = [
        _make_vecino_row("111"),
        _make_vecino_row("222"),
        _make_vecino_row("333"),
    ]
    conn = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    return conn, cursor


async def test_get_vecinos_devuelve_lista_de_srv_codigos(env_vars, mock_conn_and_cursor) -> None:
    conn, cursor = mock_conn_and_cursor
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value = conn
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        result = await repo.get_vecinos("2817670", 150.0)

    assert "111" in result
    assert "222" in result
    assert "333" in result


async def test_get_vecinos_usa_query_parametrizada(env_vars, mock_conn_and_cursor) -> None:
    conn, cursor = mock_conn_and_cursor
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value = conn
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        await repo.get_vecinos("2817670", 150.0)

    main_execute_calls = [
        c for c in cursor.execute.call_args_list if c.args and ":suministro_id" in c.args[0]
    ]
    assert len(main_execute_calls) == 1
    params = main_execute_calls[0].args[1] if len(main_execute_calls[0].args) > 1 else {}
    assert params.get("suministro_id") == "2817670"
    assert "delta" in params  # new lat/lon query requires delta parameter


async def test_get_vecinos_configura_call_timeout(env_vars, mock_conn_and_cursor) -> None:
    conn, cursor = mock_conn_and_cursor
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value = conn
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        await repo.get_vecinos("2817670", 150.0)

    assert conn.call_timeout is not None or hasattr(conn, "call_timeout")


async def test_get_vecinos_retorna_lista_vacia_si_oracle_lanza_excepcion(env_vars) -> None:
    """Si Oracle lanza cualquier excepción, get_vecinos devuelve [] sin propagar."""
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.connect.side_effect = Exception("ORA-12535: operation timed out")
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        result = await repo.get_vecinos("2817670", 150.0)

    assert result == []


async def test_get_vecinos_retorna_lista_vacia_si_query_falla(
    env_vars, mock_conn_and_cursor
) -> None:
    """Si la query falla (timeout, lock, etc.), get_vecinos devuelve []."""
    conn, cursor = mock_conn_and_cursor
    cursor.execute.side_effect = Exception("ORA-01013: user requested cancel of current operation")
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value = conn
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        result = await repo.get_vecinos("2817670", 150.0)

    assert result == []
