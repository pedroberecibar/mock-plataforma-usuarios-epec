"""TDD tests para ObtenerComparacionHistoricaUseCase.

Semántica de datos faltantes: cada período devuelve lista vacía cuando
no hay datos — el frontend detecta ausencia por len(serie)==0.
total_kwh es None cuando la serie está vacía.
"""

from datetime import date

from application.use_cases.obtener_comparacion_historica import (
    ObtenerComparacionHistoricaUseCase,
)
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository


async def _repo_con_junio_2026() -> FakeConsumoDiarioRepository:
    repo = FakeConsumoDiarioRepository()
    # Mes actual: junio 2026
    for dia in range(1, 16):
        await repo.upsert_consumo("S1", date(2026, 6, dia), 10.0)
    # Mes anterior: mayo 2026
    for dia in range(1, 32):
        await repo.upsert_consumo("S1", date(2026, 5, dia), 8.0)
    # Mismo mes año anterior: junio 2025
    for dia in range(1, 31):
        await repo.upsert_consumo("S1", date(2025, 6, dia), 12.0)
    return repo


async def test_devuelve_tres_periodos() -> None:
    repo = await _repo_con_junio_2026()
    uc = ObtenerComparacionHistoricaUseCase(repo)

    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.mes_actual.mes == date(2026, 6, 1)
    assert resultado.mes_anterior.mes == date(2026, 5, 1)
    assert resultado.mismo_mes_anio_anterior.mes == date(2025, 6, 1)


async def test_total_kwh_suma_correctamente() -> None:
    repo = await _repo_con_junio_2026()
    uc = ObtenerComparacionHistoricaUseCase(repo)

    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    # 15 días × 10 kWh = 150 kWh en junio 2026
    assert resultado.mes_actual.total_kwh == 150.0
    # 31 días × 8 kWh = 248 kWh en mayo 2026
    assert resultado.mes_anterior.total_kwh == 248.0
    # 30 días × 12 kWh = 360 kWh en junio 2025
    assert resultado.mismo_mes_anio_anterior.total_kwh == 360.0


async def test_periodo_sin_datos_devuelve_lista_vacia_y_total_none() -> None:
    repo = FakeConsumoDiarioRepository()
    # Solo tiene datos en mes actual
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.mes_actual.serie != []
    assert resultado.mes_anterior.serie == []
    assert resultado.mes_anterior.total_kwh is None
    assert resultado.mismo_mes_anio_anterior.serie == []
    assert resultado.mismo_mes_anio_anterior.total_kwh is None


async def test_datos_hasta_refleja_ultima_fecha_global() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 15), 10.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.datos_hasta == date(2026, 6, 15)


async def test_mes_parametro_normalizado_a_primer_dia() -> None:
    """Aceptar cualquier día del mes — normaliza al primer día."""
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 5), 10.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    # Se pasa el 15 del mes, debe tratarse como si fuera el 1
    resultado_15 = await uc.ejecutar("S1", mes=date(2026, 6, 15))
    resultado_1 = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado_15.mes_actual.mes == resultado_1.mes_actual.mes


async def test_aislado_por_suministro() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)
    await repo.upsert_consumo("S2", date(2026, 6, 1), 99.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert all(kwh != 99.0 for _, kwh in resultado.mes_actual.serie)
