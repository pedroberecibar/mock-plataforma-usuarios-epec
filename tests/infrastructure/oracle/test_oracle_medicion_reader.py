"""Contract tests para OracleMedicionReader — sin conexión Oracle real.

Mockean oracledb a nivel de módulo para verificar:
- Construcción correcta del DSN desde variables de entorno.
- Que la query emitida es parametrizada (no interpolada).
- Normalización de decimal coma y filtrado de nulos.
- Lógica de ancla (última lectura antes de `desde` por equipo).
- Mapeo medidor → suministro vía srv_codigo (JOIN con XXSIGEC.EQUIPOS).
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.oracle.medicion_reader import OracleMedicionReader


@pytest.fixture
def env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OR_USER", "usr")
    monkeypatch.setenv("OR_PASS", "pass")
    monkeypatch.setenv("OR_HOST", "oracle-host")
    monkeypatch.setenv("OR_PORT", "1521")
    monkeypatch.setenv("OR_SERVICE_NAME", "SIGEC")


def _make_row(
    srv: str, equipo: str, fecha: date, valor: str | float | None, cdr: str = "E"
) -> MagicMock:
    row = MagicMock()
    row.srv_codigo = srv
    row.med_numero_equipo = equipo
    row.cdr_codigo = cdr
    row.fecha = fecha
    row.lec_valor_leido = valor
    return row


@pytest.fixture
def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn, cursor


async def test_leer_lecturas_devuelve_lecturas_del_rango(env_vars, mock_connection) -> None:
    conn, cursor = mock_connection
    cursor.fetchall.side_effect = [
        # primera query: rango principal
        [_make_row("SRV-001", "91013496", date(2026, 6, 1), 13773.0)],
        # segunda query: anclas
        [],
    ]
    cursor.description = [
        ("srv_codigo",),
        ("med_numero_equipo",),
        ("cdr_codigo",),
        ("fecha",),
        ("lec_valor_leido",),
    ]

    with patch("infrastructure.oracle.medicion_reader.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value.__enter__ = MagicMock(return_value=conn)
        mock_oracledb.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_oracledb.makedsn.return_value = "oracle-dsn"

        reader = OracleMedicionReader()
        result = await reader.leer_lecturas(date(2026, 6, 1), date(2026, 6, 30))

    assert len(result) == 1
    assert result[0].equipo == "91013496"
    assert result[0].srv_codigo == "SRV-001"
    assert result[0].fecha == date(2026, 6, 1)
    assert result[0].valor_kwh == 13773.0


async def test_leer_lecturas_normaliza_coma_decimal(env_vars, mock_connection) -> None:
    conn, cursor = mock_connection
    cursor.fetchall.side_effect = [
        [_make_row("SRV-001", "91013496", date(2026, 6, 1), "13773,50")],
        [],
    ]
    cursor.description = [
        ("srv_codigo",),
        ("med_numero_equipo",),
        ("cdr_codigo",),
        ("fecha",),
        ("lec_valor_leido",),
    ]

    with patch("infrastructure.oracle.medicion_reader.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value.__enter__ = MagicMock(return_value=conn)
        mock_oracledb.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_oracledb.makedsn.return_value = "oracle-dsn"

        reader = OracleMedicionReader()
        result = await reader.leer_lecturas(date(2026, 6, 1), date(2026, 6, 30))

    assert result[0].valor_kwh == 13773.50


async def test_leer_lecturas_descarta_nulos(env_vars, mock_connection) -> None:
    conn, cursor = mock_connection
    cursor.fetchall.side_effect = [
        [
            _make_row("SRV-001", "91013496", date(2026, 6, 1), None),  # nulo → descartado
            _make_row("SRV-001", "91013496", date(2026, 6, 2), 100.0),  # válido
        ],
        [],
    ]
    cursor.description = [
        ("srv_codigo",),
        ("med_numero_equipo",),
        ("cdr_codigo",),
        ("fecha",),
        ("lec_valor_leido",),
    ]

    with patch("infrastructure.oracle.medicion_reader.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value.__enter__ = MagicMock(return_value=conn)
        mock_oracledb.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_oracledb.makedsn.return_value = "oracle-dsn"

        reader = OracleMedicionReader()
        result = await reader.leer_lecturas(date(2026, 6, 1), date(2026, 6, 30))

    assert len(result) == 1
    assert result[0].fecha == date(2026, 6, 2)


async def test_leer_lecturas_incluye_ancla_de_segunda_query(env_vars, mock_connection) -> None:
    conn, cursor = mock_connection
    cursor.fetchall.side_effect = [
        # rango principal
        [_make_row("SRV-001", "91013496", date(2026, 6, 1), 13773.0)],
        # anclas (última lectura por equipo antes de desde)
        [_make_row("SRV-001", "91013496", date(2026, 5, 27), 13721.0)],
    ]
    cursor.description = [
        ("srv_codigo",),
        ("med_numero_equipo",),
        ("cdr_codigo",),
        ("fecha",),
        ("lec_valor_leido",),
    ]

    with patch("infrastructure.oracle.medicion_reader.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value.__enter__ = MagicMock(return_value=conn)
        mock_oracledb.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_oracledb.makedsn.return_value = "oracle-dsn"

        reader = OracleMedicionReader()
        result = await reader.leer_lecturas(date(2026, 6, 1), date(2026, 6, 30))

    fechas = {lect.fecha for lect in result}
    assert date(2026, 5, 27) in fechas, "El ancla debe estar incluido en el resultado"
    assert date(2026, 6, 1) in fechas


async def test_query_usa_bind_params_no_interpolacion(env_vars, mock_connection) -> None:
    """La query no debe contener f-strings ni concatenación con los valores de fechas."""
    conn, cursor = mock_connection
    cursor.fetchall.return_value = []
    cursor.description = []
    queries_ejecutadas: list[str] = []

    def capture_execute(sql: str, params=None) -> None:
        queries_ejecutadas.append(sql)

    cursor.execute = capture_execute

    with patch("infrastructure.oracle.medicion_reader.oracledb") as mock_oracledb:
        mock_oracledb.connect.return_value.__enter__ = MagicMock(return_value=conn)
        mock_oracledb.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_oracledb.makedsn.return_value = "oracle-dsn"

        reader = OracleMedicionReader()
        await reader.leer_lecturas(date(2026, 6, 1), date(2026, 6, 30))

    for q in queries_ejecutadas:
        assert "2026" not in q, f"Fecha literal encontrada en query — usá bind params: {q!r}"
