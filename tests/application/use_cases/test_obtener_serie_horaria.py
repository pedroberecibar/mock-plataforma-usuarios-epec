"""Tests TDD para ObtenerSerieHorariaUseCase."""

from datetime import date

from application.use_cases.obtener_serie_horaria import ObtenerSerieHorariaUseCase
from infrastructure.fakes.consumo_horario_repository import FakeConsumoHorarioRepository

D = date(2026, 6, 10)


async def test_fecha_sin_datos_retorna_lista_vacia() -> None:
    repo = FakeConsumoHorarioRepository()
    resultado = await ObtenerSerieHorariaUseCase(repo).ejecutar("SRV-1", D)
    assert resultado.puntos == []
    assert resultado.fecha == D


async def test_retorna_puntos_ordenados_por_hora() -> None:
    repo = FakeConsumoHorarioRepository()
    await repo.upsert_consumo_horario("SRV-1", D, 5, 0.4)
    await repo.upsert_consumo_horario("SRV-1", D, 2, 0.2)
    await repo.upsert_consumo_horario("SRV-1", D, 20, 0.9)

    resultado = await ObtenerSerieHorariaUseCase(repo).ejecutar("SRV-1", D)

    horas = [h for h, _ in resultado.puntos]
    assert horas == sorted(horas)
    assert len(resultado.puntos) == 3


async def test_solo_retorna_datos_del_suministro_solicitado() -> None:
    repo = FakeConsumoHorarioRepository()
    await repo.upsert_consumo_horario("SRV-1", D, 10, 0.5)
    await repo.upsert_consumo_horario("SRV-2", D, 10, 9.9)

    resultado = await ObtenerSerieHorariaUseCase(repo).ejecutar("SRV-1", D)

    kwhs = [kwh for _, kwh in resultado.puntos]
    assert all(kwh < 1.0 for kwh in kwhs)
