"""TDD tests para CalcularProyeccionMensualUseCase."""

from datetime import date

import pytest

from application.use_cases.calcular_proyeccion_mensual import CalcularProyeccionMensualUseCase
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.proyeccion_repository import FakeProyeccionRepository


async def _seed_mes(
    repo: FakeConsumoDiarioRepository,
    suministro_id: str,
    year: int,
    month: int,
    kwh_por_dia: float,
    dias: int,
) -> None:
    for dia in range(1, dias + 1):
        await repo.upsert_consumo(suministro_id, date(year, month, dia), kwh_por_dia)


# ---------------------------------------------------------------------------
# Método insuficiente (< 7 días en el mes actual)
# ---------------------------------------------------------------------------


async def test_insuficiente_cuando_hay_menos_de_7_dias() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 6)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "insuficiente"
    assert result.bandera_confianza == "sin_datos"
    assert result.rango_inferior_kwh is None
    assert result.rango_superior_kwh is None


async def test_insuficiente_cuando_no_hay_datos_en_el_mes() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "insuficiente"
    assert result.rango_inferior_kwh is None


# ---------------------------------------------------------------------------
# Método reciente (≥ 7 días en el mes actual, sin historia suficiente)
# ---------------------------------------------------------------------------


async def test_reciente_cuando_hay_exactamente_7_dias() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 7)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "reciente"
    assert result.bandera_confianza == "baja"
    assert result.rango_inferior_kwh is not None
    assert result.rango_superior_kwh is not None


async def test_reciente_proyecta_tasa_diaria_por_dias_del_mes() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    # 10 kWh/día × 30 días = 300 kWh proyectados para junio
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 10)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "reciente"
    # 10 kwh/día * 30 días = 300; banda ±20% → [240, 360]
    assert result.rango_inferior_kwh == pytest.approx(240.0, rel=0.01)
    assert result.rango_superior_kwh == pytest.approx(360.0, rel=0.01)


async def test_reciente_usa_ultimos_7_dias_de_datos() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    # Primeros 3 días: 5 kWh; últimos 7 días: 20 kWh
    await _seed_mes(consumo, "S1", 2026, 6, 5.0, 3)
    for dia in range(4, 11):
        await consumo.upsert_consumo("S1", date(2026, 6, dia), 20.0)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "reciente"
    # últimos 7 días (4 al 10): 20 kWh/día → 20 * 30 = 600; banda -20% = 480
    assert result.rango_inferior_kwh == pytest.approx(480.0, rel=0.01)


# ---------------------------------------------------------------------------
# Método estacional (datos en ≥ 2 años anteriores, sin interanual)
# ---------------------------------------------------------------------------


async def test_estacional_cuando_hay_datos_en_2_anios_anteriores() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    # Datos en junio 2023 y junio 2024 (20+ días — estacional califica)
    await _seed_mes(consumo, "S1", 2023, 6, 10.0, 25)
    await _seed_mes(consumo, "S1", 2024, 6, 12.0, 25)
    # Junio 2025 (año anterior): pocos días → no califica para interanual
    await _seed_mes(consumo, "S1", 2025, 6, 11.0, 5)
    # Datos parciales en junio 2026 (7 días)
    await _seed_mes(consumo, "S1", 2026, 6, 11.0, 7)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "estacional"
    assert result.bandera_confianza == "media"
    assert result.rango_inferior_kwh is not None
    assert result.rango_superior_kwh is not None


async def test_estacional_proyeccion_dentro_de_banda_15pct() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    # Junio 2023: 10 kWh/día × 25 días = 250 kWh
    await _seed_mes(consumo, "S1", 2023, 6, 10.0, 25)
    # Junio 2024: 10 kWh/día × 25 días = 250 kWh
    await _seed_mes(consumo, "S1", 2024, 6, 10.0, 25)
    # Junio 2025: pocos días → no califica para interanual
    await _seed_mes(consumo, "S1", 2025, 6, 10.0, 5)
    # 7 días en 2026
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 7)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "estacional"
    # promedio historico (2023+2024) = 250 kWh; banda ±15% → [212.5, 287.5]
    assert result.rango_inferior_kwh == pytest.approx(250.0 * 0.85, rel=0.01)
    assert result.rango_superior_kwh == pytest.approx(250.0 * 1.15, rel=0.01)


# ---------------------------------------------------------------------------
# Método interanual (mismo mes año anterior completo)
# ---------------------------------------------------------------------------


async def test_interanual_cuando_hay_datos_del_mismo_mes_anio_anterior() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    # Junio 2025: 20 días completos
    await _seed_mes(consumo, "S1", 2025, 6, 10.0, 20)
    # Junio 2026: 10 días parciales
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 10)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "interanual"
    assert result.bandera_confianza == "alta"
    assert result.rango_inferior_kwh is not None
    assert result.rango_superior_kwh is not None


async def test_interanual_banda_10pct() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    # Junio 2025: 10 kWh/día × 20 días = 200 kWh (se toma como total del mes pasado)
    await _seed_mes(consumo, "S1", 2025, 6, 10.0, 20)
    # Junio 2026: mismos 10 días que en 2025, misma tasa → ratio = 1.0
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 10)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "interanual"
    # ratio = (10*10) / (10*10) = 1.0; projected = 1.0 * 200 = 200; ±10% → [180, 220]
    assert result.rango_inferior_kwh == pytest.approx(200.0 * 0.9, rel=0.01)
    assert result.rango_superior_kwh == pytest.approx(200.0 * 1.1, rel=0.01)


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------


async def test_persiste_proyeccion_en_repositorio() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 10)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    await uc.ejecutar("S1", date(2026, 6, 1))

    cached = await proy_repo.get_proyeccion("S1", date(2026, 6, 1))
    assert cached is not None


async def test_cascade_interanual_tiene_prioridad_sobre_estacional() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    # Hay datos en 2024 Y 2025 (estacional calificaría)
    await _seed_mes(consumo, "S1", 2024, 6, 10.0, 25)
    # Junio 2025 completo (interanual califica)
    await _seed_mes(consumo, "S1", 2025, 6, 10.0, 25)
    # Junio 2026 parcial
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 10)

    uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.metodo_aplicado == "interanual"
