"""Tests para CalcularObjetivoSugeridoUseCase — RED phase primero.

Regla de privacidad: si n_vecinos_con_datos < 5, devolver sin_datos=True.
"""

import calendar
from datetime import date

import pytest

from application.use_cases.calcular_objetivo_sugerido import CalcularObjetivoSugeridoUseCase
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.vecinos_repository import FakeVecinosRepository

MES_ACTUAL = date(2026, 6, 1)
MES_ANIO_ANTERIOR = date(2025, 6, 1)


def _ultimo_dia(d: date) -> date:
    last = calendar.monthrange(d.year, d.month)[1]
    return date(d.year, d.month, last)


async def _seed_vecino(repo: FakeConsumoDiarioRepository, sid: str, total_kwh: float) -> None:
    """Distribuye total_kwh uniformemente en el mes del año anterior."""
    dias = calendar.monthrange(MES_ANIO_ANTERIOR.year, MES_ANIO_ANTERIOR.month)[1]
    kwh_dia = total_kwh / dias
    for d in range(1, dias + 1):
        await repo.upsert_consumo(
            sid, date(MES_ANIO_ANTERIOR.year, MES_ANIO_ANTERIOR.month, d), kwh_dia
        )


@pytest.fixture
def consumo_repo() -> FakeConsumoDiarioRepository:
    return FakeConsumoDiarioRepository()


@pytest.fixture
def vecinos_repo() -> FakeVecinosRepository:
    return FakeVecinosRepository()


# ---------------------------------------------------------------------------
# Caso normal: ≥5 vecinos con datos
# ---------------------------------------------------------------------------


async def test_calcula_promedio_con_cinco_vecinos(
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    vecinos = [f"V{i}" for i in range(5)]
    vecinos_repo._vecinos["S001"] = vecinos

    totales = [100.0, 120.0, 80.0, 160.0, 140.0]
    for sid, total in zip(vecinos, totales, strict=True):
        await _seed_vecino(consumo_repo, sid, total)

    uc = CalcularObjetivoSugeridoUseCase(vecinos_repo, consumo_repo)
    result = await uc.ejecutar("S001", MES_ACTUAL)

    assert result.sin_datos is False
    assert result.n_vecinos == 5
    expected_avg = sum(totales) / 5
    assert result.valor_kwh is not None
    assert abs(result.valor_kwh - expected_avg) < 0.01


async def test_calcula_promedio_ignorando_vecinos_sin_datos(
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    """5 vecinos geográficos pero solo 5 tienen datos → promedio válido."""
    vecinos = [f"V{i}" for i in range(7)]
    vecinos_repo._vecinos["S001"] = vecinos

    # V0..V4 tienen datos, V5 y V6 no
    totales = [100.0, 120.0, 80.0, 160.0, 140.0]
    for sid, total in zip(vecinos[:5], totales, strict=True):
        await _seed_vecino(consumo_repo, sid, total)

    uc = CalcularObjetivoSugeridoUseCase(vecinos_repo, consumo_repo)
    result = await uc.ejecutar("S001", MES_ACTUAL)

    assert result.sin_datos is False
    assert result.n_vecinos == 5


# ---------------------------------------------------------------------------
# Caso privacidad: < 5 vecinos con datos
# ---------------------------------------------------------------------------


async def test_sin_datos_cuando_menos_de_cinco_vecinos(
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    vecinos = [f"V{i}" for i in range(4)]
    vecinos_repo._vecinos["S001"] = vecinos

    for sid in vecinos:
        await _seed_vecino(consumo_repo, sid, 100.0)

    uc = CalcularObjetivoSugeridoUseCase(vecinos_repo, consumo_repo)
    result = await uc.ejecutar("S001", MES_ACTUAL)

    assert result.sin_datos is True
    assert result.valor_kwh is None
    assert result.n_vecinos == 4


async def test_sin_datos_cuando_no_hay_vecinos(
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    uc = CalcularObjetivoSugeridoUseCase(vecinos_repo, consumo_repo)
    result = await uc.ejecutar("S001", MES_ACTUAL)

    assert result.sin_datos is True
    assert result.valor_kwh is None
    assert result.n_vecinos == 0


# ---------------------------------------------------------------------------
# Caso sin datos del año anterior
# ---------------------------------------------------------------------------


async def test_sin_datos_cuando_vecinos_sin_consumo_anio_anterior(
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    """5 vecinos existen geográficamente pero ninguno tiene datos del año anterior."""
    vecinos = [f"V{i}" for i in range(5)]
    vecinos_repo._vecinos["S001"] = vecinos
    # No se inserta ningún dato de consumo

    uc = CalcularObjetivoSugeridoUseCase(vecinos_repo, consumo_repo)
    result = await uc.ejecutar("S001", MES_ACTUAL)

    assert result.sin_datos is True
    assert result.valor_kwh is None
