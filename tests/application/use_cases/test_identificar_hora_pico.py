"""Tests TDD para IdentificarHoraPicoUseCase."""

from datetime import date

from application.use_cases.identificar_hora_pico import IdentificarHoraPicoUseCase
from infrastructure.fakes.consumo_horario_repository import FakeConsumoHorarioRepository

MES = date(2026, 6, 1)


async def test_sin_datos_retorna_none() -> None:
    repo = FakeConsumoHorarioRepository()
    resultado = await IdentificarHoraPicoUseCase(repo).ejecutar("SRV-1", MES)
    assert resultado is None


async def test_hora_pico_es_la_de_mayor_consumo_promedio() -> None:
    repo = FakeConsumoHorarioRepository()
    # Dos días con consumos diferentes por hora; hora 20 domina
    for d in (date(2026, 6, 1), date(2026, 6, 2)):
        await repo.upsert_consumo_horario("SRV-1", d, 8, 0.3)
        await repo.upsert_consumo_horario("SRV-1", d, 20, 0.9)

    resultado = await IdentificarHoraPicoUseCase(repo).ejecutar("SRV-1", MES)

    assert resultado is not None
    assert resultado.hora_pico == 20


async def test_perfil_24h_tiene_exactamente_24_entradas() -> None:
    repo = FakeConsumoHorarioRepository()
    for h in range(24):
        await repo.upsert_consumo_horario("SRV-1", date(2026, 6, 1), h, float(h) * 0.1)

    resultado = await IdentificarHoraPicoUseCase(repo).ejecutar("SRV-1", MES)

    assert resultado is not None
    assert len(resultado.perfil_24h) == 24
    horas = [h for h, _ in resultado.perfil_24h]
    assert horas == list(range(24))


async def test_kwh_promedio_es_media_entre_dias() -> None:
    repo = FakeConsumoHorarioRepository()
    await repo.upsert_consumo_horario("SRV-1", date(2026, 6, 1), 10, 0.4)
    await repo.upsert_consumo_horario("SRV-1", date(2026, 6, 2), 10, 0.6)

    resultado = await IdentificarHoraPicoUseCase(repo).ejecutar("SRV-1", MES)

    assert resultado is not None
    assert resultado.hora_pico == 10
    assert abs(resultado.kwh_promedio - 0.5) < 0.01


async def test_solo_considera_datos_del_mes_solicitado() -> None:
    repo = FakeConsumoHorarioRepository()
    # Hora 5 con consumo alto en julio (fuera de mes)
    await repo.upsert_consumo_horario("SRV-1", date(2026, 7, 1), 5, 9.9)
    # Hora 20 con consumo bajo en junio
    await repo.upsert_consumo_horario("SRV-1", date(2026, 6, 15), 20, 0.3)

    resultado = await IdentificarHoraPicoUseCase(repo).ejecutar("SRV-1", MES)

    assert resultado is not None
    assert resultado.hora_pico == 20  # dato de julio ignorado
