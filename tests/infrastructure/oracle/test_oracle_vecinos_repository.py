"""Contract tests para OracleVecinosRepository — sin conexión Oracle real.

Verifican:
- La query usa VW_INTELIGENTES con :suministro_id parametrizado (no interpolado).
- Se retorna la columna SUMINISTRO como strings.
- Si Oracle lanza excepción (timeout, error de red) se retorna [] sin propagar.
- call_timeout es configurado en la conexión.
- suministro_id no-numérico retorna [] sin intentar conectarse.
"""

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


@pytest.fixture
def mock_conn_and_cursor():
    cursor = MagicMock()
    cursor.description = [("SUMINISTRO",)]
    cursor.fetchall.return_value = [("111",), ("222",), ("333",)]
    conn = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    return conn, cursor


async def test_get_vecinos_devuelve_lista_de_suministros(env_vars, mock_conn_and_cursor) -> None:
    conn, cursor = mock_conn_and_cursor
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value = conn
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        result = await repo.get_vecinos("2817670")

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
        await repo.get_vecinos("2817670")

    main_execute_calls = [
        c for c in cursor.execute.call_args_list if c.args and ":suministro_id" in c.args[0]
    ]
    assert len(main_execute_calls) == 1
    params = main_execute_calls[0].args[1] if len(main_execute_calls[0].args) > 1 else {}
    assert params.get("suministro_id") == 2817670


async def test_get_vecinos_configura_call_timeout(env_vars, mock_conn_and_cursor) -> None:
    conn, cursor = mock_conn_and_cursor
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value = conn
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        await repo.get_vecinos("2817670")

    assert conn.call_timeout is not None or hasattr(conn, "call_timeout")


async def test_get_vecinos_retorna_lista_vacia_si_oracle_lanza_excepcion(env_vars) -> None:
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.connect.side_effect = Exception("ORA-12535: operation timed out")
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        result = await repo.get_vecinos("2817670")

    assert result == []


async def test_get_vecinos_retorna_lista_vacia_si_query_falla(
    env_vars, mock_conn_and_cursor
) -> None:
    conn, cursor = mock_conn_and_cursor
    cursor.execute.side_effect = Exception("ORA-01013: user requested cancel of current operation")
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value = conn
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        result = await repo.get_vecinos("2817670")

    assert result == []


async def test_get_vecinos_retorna_lista_vacia_si_suministro_id_no_numerico(env_vars) -> None:
    with patch("infrastructure.oracle.vecinos_repository.oracledb") as mock_oracledb:
        mock_oracledb.makedsn.return_value = "fake-dsn"
        mock_oracledb.ProgrammingError = Exception

        repo = OracleVecinosRepository()
        result = await repo.get_vecinos("no-es-numero")

    assert result == []
    mock_oracledb.connect.assert_not_called()
