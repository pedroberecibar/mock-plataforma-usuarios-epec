"""TDD tests para ObtenerSerieDiariaUseCase."""

from datetime import date

from application.use_cases.obtener_serie_diaria import ObtenerSerieDiariaUseCase
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository


async def test_devuelve_serie_en_rango_solicitado() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)
    await repo.upsert_consumo("S1", date(2026, 6, 2), 12.0)
    await repo.upsert_consumo("S1", date(2026, 6, 3), 8.0)

    uc = ObtenerSerieDiariaUseCase(repo)
    resultado = await uc.ejecutar("S1", date(2026, 6, 1), date(2026, 6, 2))

    assert resultado.serie == [(date(2026, 6, 1), 10.0), (date(2026, 6, 2), 12.0)]


async def test_datos_hasta_refleja_ultima_fecha_con_dato() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)
    await repo.upsert_consumo("S1", date(2026, 6, 14), 9.5)

    uc = ObtenerSerieDiariaUseCase(repo)
    resultado = await uc.ejecutar("S1", date(2026, 6, 1), date(2026, 6, 30))

    assert resultado.datos_hasta == date(2026, 6, 14)


async def test_datos_hasta_es_none_si_no_hay_ninguna_carga() -> None:
    repo = FakeConsumoDiarioRepository()

    uc = ObtenerSerieDiariaUseCase(repo)
    resultado = await uc.ejecutar("S1", date(2026, 6, 1), date(2026, 6, 30))

    assert resultado.datos_hasta is None
    assert resultado.serie == []


async def test_serie_vacia_si_no_hay_datos_en_rango() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 5, 1), 10.0)  # fuera del rango pedido

    uc = ObtenerSerieDiariaUseCase(repo)
    resultado = await uc.ejecutar("S1", date(2026, 6, 1), date(2026, 6, 30))

    assert resultado.serie == []
    # datos_hasta refleja la ultima carga global, no solo el rango
    assert resultado.datos_hasta == date(2026, 5, 1)


async def test_aislado_por_suministro() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)
    await repo.upsert_consumo("S2", date(2026, 6, 1), 99.0)

    uc = ObtenerSerieDiariaUseCase(repo)
    resultado = await uc.ejecutar("S1", date(2026, 6, 1), date(2026, 6, 30))

    assert all(kwh != 99.0 for _, kwh in resultado.serie)
