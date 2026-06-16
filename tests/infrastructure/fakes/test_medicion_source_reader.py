from datetime import date

from domain.lecturas import LecturaTelemedida
from infrastructure.fakes.medicion_source_reader import SEED_LECTURAS_EPEC, FakeMedicionSourceReader


def _lectura(equipo: str, fecha: date, valor_kwh: float, cdr: str = "E") -> LecturaTelemedida:
    return LecturaTelemedida(equipo=equipo, cdr_codigo=cdr, fecha=fecha, valor_kwh=valor_kwh)


async def test_leer_lecturas_devuelve_rango_solicitado() -> None:
    reader = FakeMedicionSourceReader(
        lecturas=[
            _lectura("E1", date(2026, 1, 1), 1000.0),
            _lectura("E1", date(2026, 2, 1), 1200.0),
            _lectura("E1", date(2026, 3, 1), 1450.0),
        ]
    )

    result = await reader.leer_lecturas(date(2026, 2, 1), date(2026, 2, 28))

    fechas = {lect.fecha for lect in result}
    assert date(2026, 2, 1) in fechas
    assert date(2026, 3, 1) not in fechas


async def test_leer_lecturas_incluye_ancla_por_equipo() -> None:
    """La última lectura antes de `desde` por equipo debe incluirse como ancla."""
    reader = FakeMedicionSourceReader(
        lecturas=[
            _lectura("E1", date(2026, 1, 10), 900.0),
            _lectura("E1", date(2026, 1, 25), 950.0),  # ancla más reciente para E1
            _lectura("E1", date(2026, 2, 5), 1000.0),
            _lectura("E2", date(2026, 1, 20), 2000.0),  # ancla para E2
            _lectura("E2", date(2026, 2, 10), 2100.0),
        ]
    )

    result = await reader.leer_lecturas(date(2026, 2, 1), date(2026, 2, 28))

    ancla_e1 = next(
        (lect for lect in result if lect.equipo == "E1" and lect.fecha == date(2026, 1, 25)), None
    )
    ancla_e2 = next(
        (lect for lect in result if lect.equipo == "E2" and lect.fecha == date(2026, 1, 20)), None
    )
    assert ancla_e1 is not None, "Debe incluirse la ancla de E1 (Jan 25)"
    assert ancla_e2 is not None, "Debe incluirse la ancla de E2 (Jan 20)"

    # La lectura más antigua de E1 en enero NO debe aparecer
    assert not any(lect.equipo == "E1" and lect.fecha == date(2026, 1, 10) for lect in result)


async def test_leer_lecturas_ancla_solo_la_mas_reciente_por_equipo() -> None:
    """Solo se devuelve UN ancla por equipo (la última antes de `desde`)."""
    reader = FakeMedicionSourceReader(
        lecturas=[
            _lectura("E1", date(2026, 1, 1), 100.0),
            _lectura("E1", date(2026, 1, 15), 150.0),
            _lectura("E1", date(2026, 1, 31), 200.0),  # esta es la ancla
            _lectura("E1", date(2026, 2, 15), 250.0),
        ]
    )

    result = await reader.leer_lecturas(date(2026, 2, 1), date(2026, 2, 28))

    lecturas_e1_pre_desde = [
        lect for lect in result if lect.equipo == "E1" and lect.fecha < date(2026, 2, 1)
    ]
    assert len(lecturas_e1_pre_desde) == 1
    assert lecturas_e1_pre_desde[0].fecha == date(2026, 1, 31)


async def test_leer_lecturas_sin_historial_previo_no_falla() -> None:
    """Si no hay lecturas antes de `desde`, devuelve solo el rango sin error."""
    reader = FakeMedicionSourceReader(
        lecturas=[
            _lectura("E1", date(2026, 6, 1), 1000.0),
            _lectura("E1", date(2026, 6, 15), 1100.0),
        ]
    )

    result = await reader.leer_lecturas(date(2026, 6, 1), date(2026, 6, 30))

    assert len(result) == 2
    assert not any(lect.fecha < date(2026, 6, 1) for lect in result)


async def test_seed_tiene_datos_representativos() -> None:
    """El seed cubre múltiples equipos, gap, cdr != E, y duplicado."""
    equipos = {lect.equipo for lect in SEED_LECTURAS_EPEC}
    assert len(equipos) >= 2

    codigos = {lect.cdr_codigo for lect in SEED_LECTURAS_EPEC}
    assert "E" in codigos
    assert len(codigos) >= 2, "El seed debe incluir lecturas con cdr_codigo != 'E'"

    e1_lecturas = sorted(
        (
            lect
            for lect in SEED_LECTURAS_EPEC
            if lect.equipo == next(iter(equipos)) and lect.cdr_codigo == "E"
        ),
        key=lambda lect: lect.fecha,
    )
    fechas = [lect.fecha for lect in e1_lecturas]
    gaps = [(fechas[i + 1] - fechas[i]).days for i in range(len(fechas) - 1)]
    assert any(g > 2 for g in gaps), "El seed debe tener al menos un gap de más de 2 días"


async def test_seed_reader_incluye_ancla_en_consulta_parcial() -> None:
    """Usando el seed, una consulta de junio debe incluir ancla de mayo."""
    reader = FakeMedicionSourceReader(lecturas=SEED_LECTURAS_EPEC)

    result = await reader.leer_lecturas(date(2026, 6, 1), date(2026, 6, 30))

    anclas = [lect for lect in result if lect.fecha < date(2026, 6, 1)]
    assert len(anclas) >= 1, "Debe haber al menos un ancla por equipo desde el historial del seed"
