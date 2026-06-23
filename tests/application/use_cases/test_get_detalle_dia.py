"""Tests para GetDetalleDiaUseCase — RED phase.

Casos:
  1. Día con datos propios + ≥5 vecinos → todos los campos completos
  2. Día sin datos propios → kwh_dia=None, resto puede estar
  3. <5 vecinos con datos → kwh_promedio_zona=None (privacidad Ley 25.326)
"""

from datetime import date, timedelta

import pytest

from application.use_cases.get_detalle_dia import DetalleDiaResult, GetDetalleDiaUseCase
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.vecinos_repository import FakeVecinosRepository

# Día de referencia: un viernes de 2026
FECHA = date(2026, 6, 19)  # viernes
FECHA_ANT = FECHA - timedelta(days=364)  # mismo día-de-semana año anterior


@pytest.fixture
def consumo_repo() -> FakeConsumoDiarioRepository:
    return FakeConsumoDiarioRepository()


@pytest.fixture
def vecinos_repo() -> FakeVecinosRepository:
    return FakeVecinosRepository()


# ---------------------------------------------------------------------------
# Caso 1: día con datos propios + ≥5 vecinos
# ---------------------------------------------------------------------------


async def test_detalle_dia_completo(
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    """Devuelve todos los campos cuando hay datos propios y ≥5 vecinos."""
    await consumo_repo.upsert_consumo("S001", FECHA, 12.5)
    await consumo_repo.upsert_consumo("S001", FECHA_ANT, 10.0)

    vecinos = [f"V{i}" for i in range(5)]
    vecinos_repo._vecinos["S001"] = vecinos
    kwh_vecinos = [8.0, 9.0, 11.0, 10.5, 9.5]
    for vid, kwh in zip(vecinos, kwh_vecinos, strict=True):
        await consumo_repo.upsert_consumo(vid, FECHA, kwh)

    uc = GetDetalleDiaUseCase(consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", FECHA)

    assert isinstance(result, DetalleDiaResult)
    assert result.fecha == FECHA
    assert result.kwh_dia == pytest.approx(12.5)
    assert result.kwh_mismo_dia_anio_ant == pytest.approx(10.0)
    assert result.n_vecinos == 5
    assert result.kwh_promedio_zona is not None
    expected_prom = sum(kwh_vecinos) / 5
    assert result.kwh_promedio_zona == pytest.approx(expected_prom)


# ---------------------------------------------------------------------------
# Caso 2: día sin datos propios
# ---------------------------------------------------------------------------


async def test_detalle_dia_sin_consumo_propio(
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    """kwh_dia=None cuando el suministro no tiene dato para esa fecha."""
    # 5 vecinos con datos para que promedio no sea None
    vecinos = [f"V{i}" for i in range(5)]
    vecinos_repo._vecinos["S001"] = vecinos
    for vid in vecinos:
        await consumo_repo.upsert_consumo(vid, FECHA, 10.0)

    uc = GetDetalleDiaUseCase(consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", FECHA)

    assert result.kwh_dia is None
    assert result.kwh_mismo_dia_anio_ant is None
    assert result.n_vecinos == 5
    assert result.kwh_promedio_zona is not None


# ---------------------------------------------------------------------------
# Caso 3: <5 vecinos → privacidad → kwh_promedio_zona=None
# ---------------------------------------------------------------------------


async def test_detalle_dia_privacidad_menos_de_cinco_vecinos(
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    """kwh_promedio_zona=None cuando hay menos de 5 vecinos con datos."""
    await consumo_repo.upsert_consumo("S001", FECHA, 12.5)

    vecinos = [f"V{i}" for i in range(4)]  # solo 4
    vecinos_repo._vecinos["S001"] = vecinos
    for vid in vecinos:
        await consumo_repo.upsert_consumo(vid, FECHA, 10.0)

    uc = GetDetalleDiaUseCase(consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", FECHA)

    assert result.kwh_promedio_zona is None
    assert result.n_vecinos == 4
