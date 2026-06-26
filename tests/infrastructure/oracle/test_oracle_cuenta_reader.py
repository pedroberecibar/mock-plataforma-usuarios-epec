import datetime as dt

from infrastructure.oracle.cuenta_reader import _row_to_raw


def _row() -> list[object]:
    return [
        "PALACIOS NATALIA",  # RAZON_SOCIAL
        "DNI",  # TIPO_DOCUMENTO
        24241815,  # NRO_DOCUMENTO (NUMBER)
        27242418153,  # CUIT (NUMBER)
        "SAN MARTIN",  # CALLE
        100,  # ALTURA (NUMBER)
        "3",  # PISO
        "B",  # DEPTO
        None,  # TORRE
        "CENTRO",  # BARRIO
        "CORDOBA",  # LOCALIDAD
        5000,  # CP (NUMBER)
        None,  # DATOS_ADICIONALES_DOMICILIO
        "SN",  # ESTADO_SERVICIO
        "NANSEN",  # TELEMEDIBLE
        "91013486",  # MEDIDOR
        dt.datetime(2023, 3, 10, 0, 0),  # TELEMEDIBLE_DESDE
        "140",  # CODIGO_TARIFA
        "1.a/f RESIDENCIAL",  # TARIFA
        "1",  # GRUPO_TARIFARIO
        "1",  # CLASE
        "1 a-b-f Casas de familia",  # DESCRIPCION_CLASE
        "1",  # TENSION
        "TRI",  # MEDIDOR_FASES
    ]


def test_mapea_numbers_a_str() -> None:
    raw = _row_to_raw(_row())
    assert raw.nro_documento == "24241815"
    assert raw.cuit == "27242418153"
    assert raw.altura == "100"
    assert raw.cp == "5000"


def test_mapea_fecha_a_date() -> None:
    raw = _row_to_raw(_row())
    assert raw.telemedible_desde == dt.date(2023, 3, 10)


def test_campos_none_quedan_none() -> None:
    row = _row()
    row[8] = None  # TORRE
    row[23] = None  # MEDIDOR_FASES
    raw = _row_to_raw(row)
    assert raw.torre is None
    assert raw.medidor_fases is None
