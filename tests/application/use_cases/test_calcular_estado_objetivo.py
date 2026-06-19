"""Tests para CalcularEstadoObjetivoUseCase — RED phase.

Cubre los 4 valores de texto_dinamico:
  bajo_ritmo   — días_objetivo_consumidos < días_transcurridos - 5%
  en_ritmo     — dentro de ±5%
  sobre_ritmo  — días_objetivo_consumidos > días_transcurridos + 5%
  agotado      — consumo_acumulado >= objetivo_kwh
Y el caso sin_objetivo.
"""

import calendar
from datetime import date

import pytest

from application.use_cases.calcular_estado_objetivo import CalcularEstadoObjetivoUseCase
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.objetivo_consumo_repository import FakeObjetivoConsumoRepository
from infrastructure.fakes.vecinos_repository import FakeVecinosRepository

MES = date(2026, 6, 1)  # 30 días

# En junio 2026, simularemos que "hoy" es el día 15 (15 días transcurridos)
HOY = date(2026, 6, 15)
OBJETIVO_KWH = 300.0
RITMO_DIARIO = OBJETIVO_KWH / 30  # 10 kWh/día


@pytest.fixture
def objetivo_repo() -> FakeObjetivoConsumoRepository:
    return FakeObjetivoConsumoRepository()


@pytest.fixture
def consumo_repo() -> FakeConsumoDiarioRepository:
    return FakeConsumoDiarioRepository()


@pytest.fixture
def vecinos_repo() -> FakeVecinosRepository:
    return FakeVecinosRepository()


async def _set_objetivo(repo: FakeObjetivoConsumoRepository) -> None:
    await repo.upsert_objetivo("S001", OBJETIVO_KWH, "manual", date(2026, 6, 1))


async def _seed_consumo_diario(repo: FakeConsumoDiarioRepository, kwh_por_dia: float) -> None:
    """Inserta consumo uniforme del día 1 al 14 (el 15 es el último sin dato todavía)."""
    for d in range(1, 15):
        await repo.upsert_consumo("S001", date(2026, 6, d), kwh_por_dia)


# ---------------------------------------------------------------------------
# sin_objetivo
# ---------------------------------------------------------------------------


async def test_sin_objetivo_devuelve_sin_objetivo(
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    uc = CalcularEstadoObjetivoUseCase(objetivo_repo, consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", MES, hoy=HOY)

    assert result.texto_dinamico == "sin_objetivo"
    assert result.objetivo_kwh is None


# ---------------------------------------------------------------------------
# bajo_ritmo: consumo acumulado menor al ritmo esperado (margen > 5%)
# ---------------------------------------------------------------------------


async def test_bajo_ritmo(
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    await _set_objetivo(objetivo_repo)
    # 14 días × 7 kWh = 98 kWh acumulado
    # ritmo_diario = 10 kWh/día → días_objetivo_consumidos = 98/10 = 9.8
    # días_transcurridos = 15
    # 9.8 < 15 × 0.95 = 14.25 → bajo_ritmo
    await _seed_consumo_diario(consumo_repo, 7.0)

    uc = CalcularEstadoObjetivoUseCase(objetivo_repo, consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", MES, hoy=HOY)

    assert result.texto_dinamico == "bajo_ritmo"
    assert result.excedente_kwh is None
    assert result.objetivo_kwh == OBJETIVO_KWH
    assert result.dias_transcurridos == 15
    assert result.dias_objetivo_consumidos is not None
    assert abs(result.dias_objetivo_consumidos - 9.8) < 0.1


# ---------------------------------------------------------------------------
# en_ritmo: dentro del ±5%
# ---------------------------------------------------------------------------


async def test_en_ritmo(
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    await _set_objetivo(objetivo_repo)
    # 14 días × 10.5 kWh = 147 kWh → días_objetivo_consumidos = 147/10 = 14.7
    # días_transcurridos = 15
    # 14.7 dentro de [15×0.95=14.25, 15×1.05=15.75] → en_ritmo
    await _seed_consumo_diario(consumo_repo, 10.5)

    uc = CalcularEstadoObjetivoUseCase(objetivo_repo, consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", MES, hoy=HOY)

    assert result.texto_dinamico == "en_ritmo"


# ---------------------------------------------------------------------------
# sobre_ritmo: consumo mayor al ritmo esperado (margen > 5%)
# ---------------------------------------------------------------------------


async def test_sobre_ritmo(
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    await _set_objetivo(objetivo_repo)
    # 14 días × 13 kWh = 182 kWh → días_objetivo_consumidos = 18.2
    # días_transcurridos = 15
    # 18.2 > 15×1.05=15.75 → sobre_ritmo
    await _seed_consumo_diario(consumo_repo, 13.0)

    uc = CalcularEstadoObjetivoUseCase(objetivo_repo, consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", MES, hoy=HOY)

    assert result.texto_dinamico == "sobre_ritmo"
    assert result.excedente_kwh is None


# ---------------------------------------------------------------------------
# agotado: consumo_acumulado >= objetivo_kwh
# ---------------------------------------------------------------------------


async def test_agotado(
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    await _set_objetivo(objetivo_repo)
    # 14 días × 25 kWh = 350 kWh >= 300 → agotado; excedente = 50 kWh
    await _seed_consumo_diario(consumo_repo, 25.0)

    uc = CalcularEstadoObjetivoUseCase(objetivo_repo, consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", MES, hoy=HOY)

    assert result.texto_dinamico == "agotado"
    assert result.excedente_kwh is not None
    assert abs(result.excedente_kwh - 50.0) < 0.1


# ---------------------------------------------------------------------------
# Indicador 3: consumo diario real vs objetivo
# ---------------------------------------------------------------------------


async def test_indicador_3_consumo_diario(
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    await _set_objetivo(objetivo_repo)
    # Día 13: 8 kWh, Día 14: 12 kWh — el más reciente con dato es el 14
    for d in range(1, 14):
        await consumo_repo.upsert_consumo("S001", date(2026, 6, d), 8.0)
    await consumo_repo.upsert_consumo("S001", date(2026, 6, 14), 12.0)

    uc = CalcularEstadoObjetivoUseCase(objetivo_repo, consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", MES, hoy=HOY)

    assert result.consumo_diario_real_kwh == 12.0
    assert result.consumo_diario_objetivo_kwh is not None
    assert abs(result.consumo_diario_objetivo_kwh - 10.0) < 0.01  # 300/30


# ---------------------------------------------------------------------------
# Indicador 1: diferencia_pct vs zona
# ---------------------------------------------------------------------------


async def test_indicador_1_diferencia_pct(
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    vecinos_repo: FakeVecinosRepository,
) -> None:
    await _set_objetivo(objetivo_repo)  # objetivo = 300 kWh
    # Configurar vecinos con promedio de 250 kWh en junio 2025
    vecinos = [f"V{i}" for i in range(5)]
    vecinos_repo._vecinos["S001"] = vecinos
    last_day = calendar.monthrange(2025, 6)[1]
    for vid in vecinos:
        for d in range(1, last_day + 1):
            await consumo_repo.upsert_consumo(vid, date(2025, 6, d), 250.0 / last_day)

    await _seed_consumo_diario(consumo_repo, 10.0)

    uc = CalcularEstadoObjetivoUseCase(objetivo_repo, consumo_repo, vecinos_repo)
    result = await uc.ejecutar("S001", MES, hoy=HOY)

    # diferencia_pct = (300 - 250) / 250 * 100 = 20%
    assert result.promedio_vecinos_kwh is not None
    assert result.diferencia_pct is not None
    assert abs(result.diferencia_pct - 20.0) < 0.5
