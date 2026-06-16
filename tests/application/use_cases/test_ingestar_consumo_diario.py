"""Tests TDD para IngestarConsumoDiarioUseCase.

Todos usan Fakes — sin I/O real.
"""

from datetime import date, timedelta

from application.use_cases.ingestar_consumo_diario import IngestarConsumoDiarioUseCase
from domain.lecturas import LecturaTelemedida
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.medicion_source_reader import SEED_LECTURAS_EPEC, FakeMedicionSourceReader


def _lectura(equipo: str, fecha: date, valor: float, cdr: str = "E") -> LecturaTelemedida:
    return LecturaTelemedida(equipo=equipo, cdr_codigo=cdr, fecha=fecha, valor_kwh=valor)


async def test_dos_lecturas_consecutivas_generan_tasa_uniforme() -> None:
    """L0=1000 en d0, L1=1050 en d0+5 → 5 días a 10.0 kWh/día."""
    d0 = date(2026, 6, 1)
    d1 = d0 + timedelta(days=5)
    reader = FakeMedicionSourceReader(
        lecturas=[_lectura("E1", d0, 1000.0), _lectura("E1", d1, 1050.0)]
    )
    repo = FakeConsumoDiarioRepository()

    await IngestarConsumoDiarioUseCase(reader, repo).ejecutar(d0, d1)

    serie = await repo.get_serie("E1", d0, d1)
    assert len(serie) == 5
    assert all(kwh == 10.0 for _, kwh in serie)
    fechas = [f for f, _ in serie]
    assert fechas == sorted(fechas)


async def test_ultimo_dia_lectura_no_genera_consumo() -> None:
    """El último día de la serie (sin lectura siguiente) no debe tener c(d)."""
    d0 = date(2026, 6, 1)
    d1 = date(2026, 6, 4)
    reader = FakeMedicionSourceReader(
        lecturas=[_lectura("E1", d0, 100.0), _lectura("E1", d1, 140.0)]
    )
    repo = FakeConsumoDiarioRepository()

    await IngestarConsumoDiarioUseCase(reader, repo).ejecutar(d0, d1)

    serie = await repo.get_serie("E1", d0, d1)
    fechas = {f for f, _ in serie}
    assert d1 not in fechas


async def test_hueco_distribuye_tasa_uniformemente() -> None:
    """L0=0 en d0, L1=100 en d0+10 (sin lecturas intermedias) → 10 días a 10 kWh/día."""
    d0 = date(2026, 6, 1)
    d1 = d0 + timedelta(days=10)
    reader = FakeMedicionSourceReader(lecturas=[_lectura("E1", d0, 0.0), _lectura("E1", d1, 100.0)])
    repo = FakeConsumoDiarioRepository()

    await IngestarConsumoDiarioUseCase(reader, repo).ejecutar(d0, d1)

    serie = await repo.get_serie("E1", d0, d1)
    assert len(serie) == 10
    assert all(kwh == 10.0 for _, kwh in serie)


async def test_delta_negativo_se_omite() -> None:
    """Si L_next < L_curr (reset de contador), ese intervalo no genera consumo."""
    d0, d1, d2 = date(2026, 6, 1), date(2026, 6, 5), date(2026, 6, 10)
    reader = FakeMedicionSourceReader(
        lecturas=[
            _lectura("E1", d0, 500.0),
            _lectura("E1", d1, 300.0),  # reset: valor baja
            _lectura("E1", d2, 350.0),
        ]
    )
    repo = FakeConsumoDiarioRepository()

    await IngestarConsumoDiarioUseCase(reader, repo).ejecutar(d0, d2)

    serie = await repo.get_serie("E1", d0, d2)
    # El intervalo d0→d1 tiene delta negativo: no se persiste
    assert not any(
        f in {d0, date(2026, 6, 2), date(2026, 6, 3), date(2026, 6, 4)} for f, _ in serie
    )
    # El intervalo d1→d2 tiene delta positivo: sí se persiste
    assert any(f == d1 for f, _ in serie)


async def test_dos_equipos_se_procesan_independientemente() -> None:
    """Lecturas de E1 y E2 generan series separadas sin interferencia."""
    d0, d1 = date(2026, 6, 1), date(2026, 6, 6)
    reader = FakeMedicionSourceReader(
        lecturas=[
            _lectura("E1", d0, 1000.0),
            _lectura("E1", d1, 1060.0),
            _lectura("E2", d0, 5000.0),
            _lectura("E2", d1, 5010.0),
        ]
    )
    repo = FakeConsumoDiarioRepository()

    await IngestarConsumoDiarioUseCase(reader, repo).ejecutar(d0, d1)

    serie_e1 = await repo.get_serie("E1", d0, d1)
    serie_e2 = await repo.get_serie("E2", d0, d1)

    assert all(kwh == 12.0 for _, kwh in serie_e1)
    assert all(kwh == 2.0 for _, kwh in serie_e2)


async def test_cdr_no_e_se_ignora() -> None:
    """Lecturas con cdr_codigo != 'E' no deben contribuir al cálculo."""
    d0, d1 = date(2026, 6, 1), date(2026, 6, 5)
    reader = FakeMedicionSourceReader(
        lecturas=[
            _lectura("E1", d0, 1000.0, cdr="E"),
            _lectura("E1", d0, 9999.0, cdr="R"),  # debe ignorarse
            _lectura("E1", d1, 1040.0, cdr="E"),
        ]
    )
    repo = FakeConsumoDiarioRepository()

    await IngestarConsumoDiarioUseCase(reader, repo).ejecutar(d0, d1)

    serie = await repo.get_serie("E1", d0, d1)
    assert all(kwh == 10.0 for _, kwh in serie)


async def test_dedupe_por_equipo_fecha() -> None:
    """Duplicados (mismo equipo + fecha) se deduплicан antes del cálculo."""
    d0, d1 = date(2026, 6, 1), date(2026, 6, 4)
    reader = FakeMedicionSourceReader(
        lecturas=[
            _lectura("E1", d0, 1000.0),
            _lectura("E1", d0, 1000.0),  # duplicado exacto
            _lectura("E1", d1, 1030.0),
        ]
    )
    repo = FakeConsumoDiarioRepository()

    await IngestarConsumoDiarioUseCase(reader, repo).ejecutar(d0, d1)

    serie = await repo.get_serie("E1", d0, d1)
    assert len(serie) == 3
    assert all(kwh == 10.0 for _, kwh in serie)


async def test_ancla_fuera_de_rango_permite_calcular_primer_dia() -> None:
    """Si la ancla está antes de `desde`, el primer día del rango ya tiene un 'anterior'."""
    ancla = date(2026, 5, 28)
    desde = date(2026, 6, 1)
    hasta = date(2026, 6, 6)
    reader = FakeMedicionSourceReader(
        lecturas=[
            _lectura("E1", ancla, 1000.0),  # ancla: antes del rango
            _lectura("E1", desde, 1040.0),  # primer día del rango
            _lectura("E1", hasta, 1100.0),
        ]
    )
    repo = FakeConsumoDiarioRepository()

    await IngestarConsumoDiarioUseCase(reader, repo).ejecutar(desde, hasta)

    serie = await repo.get_serie("E1", desde, hasta)
    # El intervalo ancla→desde (4 días) da rate=10 kWh/día → desde asignado con 10.0
    primer_dia = dict(serie).get(desde)
    assert primer_dia is not None


async def test_integracion_semilla_completa() -> None:
    """End-to-end: SEED_LECTURAS_EPEC → IngestarConsumoDiarioUseCase → FakeRepo.

    Verifica que la serie queda materializada con valores plausibles y sin nulos.
    """
    reader = FakeMedicionSourceReader(lecturas=SEED_LECTURAS_EPEC)
    repo = FakeConsumoDiarioRepository()

    desde, hasta = date(2026, 6, 1), date(2026, 6, 30)
    await IngestarConsumoDiarioUseCase(reader, repo).ejecutar(desde, hasta)

    serie_e1 = await repo.get_serie("91013496", desde, hasta)
    serie_e2 = await repo.get_serie("91013497", desde, hasta)

    assert len(serie_e1) > 0, "Equipo 91013496 debe tener serie en junio"
    assert len(serie_e2) > 0, "Equipo 91013497 debe tener serie en junio"
    assert all(kwh > 0 for _, kwh in serie_e1), "Todos los consumos deben ser positivos"
    assert all(kwh > 0 for _, kwh in serie_e2)

    # Las cdr='R' y duplicados no deben haber corrompido los valores
    valores_e1 = [kwh for _, kwh in serie_e1]
    assert max(valores_e1) < 1000, "Ningún día debe tener consumo anómalo (lectura R filtrada)"
