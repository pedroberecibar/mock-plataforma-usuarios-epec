"""Tests para DetectarAnomaliaConsumoUseCase.

El caso de uso detecta si el último día con dato en la serie del mes
tiene un consumo estadísticamente anómalo (z-score > umbral).

Comportamientos a verificar:
- Serie con datos suficientes, consumo normal → sin anomalía
- Serie con datos suficientes, consumo alto → anomalía detectada con desvío correcto
- Serie con menos de 3 días → sin anomalía (datos insuficientes)
- El umbral de z-score es configurable
"""

from datetime import date

import pytest

from application.use_cases.detectar_anomalia_consumo import (
    AnomaliaResult,
    DetectarAnomaliaConsumoUseCase,
)
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository


@pytest.fixture
def consumo_repo() -> FakeConsumoDiarioRepository:
    return FakeConsumoDiarioRepository()


async def test_sin_anomalia_con_consumo_normal(
    consumo_repo: FakeConsumoDiarioRepository,
) -> None:
    mes = date(2026, 6, 1)
    for d in range(1, 11):
        await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, d), 10.0)

    uc = DetectarAnomaliaConsumoUseCase(consumo_repo)
    resultado = await uc.ejecutar("SRV-001", mes)

    assert resultado is None


async def test_anomalia_detectada_con_consumo_alto(
    consumo_repo: FakeConsumoDiarioRepository,
) -> None:
    for d in range(1, 10):
        await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, d), 10.0)
    await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, 10), 40.0)

    uc = DetectarAnomaliaConsumoUseCase(consumo_repo)
    resultado = await uc.ejecutar("SRV-001", date(2026, 6, 1))

    assert resultado is not None
    assert isinstance(resultado, AnomaliaResult)
    assert resultado.fecha == date(2026, 6, 10)
    assert resultado.z_score > 2.0
    assert resultado.desviacion_pct > 0.0


async def test_desviacion_pct_refleja_exceso_sobre_promedio(
    consumo_repo: FakeConsumoDiarioRepository,
) -> None:
    for d in range(1, 10):
        await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, d), 10.0)
    await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, 10), 40.0)

    uc = DetectarAnomaliaConsumoUseCase(consumo_repo)
    resultado = await uc.ejecutar("SRV-001", date(2026, 6, 1))

    assert resultado is not None
    # mean = (9*10 + 40) / 10 = 13.0 → desviacion = (40-13)/13*100 ≈ 207.69%
    assert abs(resultado.desviacion_pct - 207.69) < 1.0


async def test_pocos_datos_no_emite_anomalia(
    consumo_repo: FakeConsumoDiarioRepository,
) -> None:
    await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, 1), 10.0)
    await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, 2), 100.0)

    uc = DetectarAnomaliaConsumoUseCase(consumo_repo)
    resultado = await uc.ejecutar("SRV-001", date(2026, 6, 1))

    assert resultado is None


async def test_umbral_configurable(
    consumo_repo: FakeConsumoDiarioRepository,
) -> None:
    for d in range(1, 10):
        await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, d), 10.0)
    await consumo_repo.upsert_consumo("SRV-001", date(2026, 6, 10), 40.0)

    uc_alto_umbral = DetectarAnomaliaConsumoUseCase(consumo_repo, umbral_z=10.0)
    resultado = await uc_alto_umbral.ejecutar("SRV-001", date(2026, 6, 1))

    assert resultado is None


async def test_sin_datos_en_mes_no_falla(
    consumo_repo: FakeConsumoDiarioRepository,
) -> None:
    uc = DetectarAnomaliaConsumoUseCase(consumo_repo)
    resultado = await uc.ejecutar("SRV-001", date(2026, 6, 1))
    assert resultado is None
