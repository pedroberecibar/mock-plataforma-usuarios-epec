"""Tests para FakeProyeccionRepository."""

from datetime import date

from domain.proyeccion import ProyeccionMensual
from infrastructure.fakes.proyeccion_repository import FakeProyeccionRepository


def _make_proyeccion(suministro_id: str = "S1", mes: date = date(2026, 6, 1)) -> ProyeccionMensual:
    return ProyeccionMensual(
        suministro_id=suministro_id,
        mes=mes,
        metodo_aplicado="reciente",
        meses_usados_como_base=0,
        dias_usados_como_base=7,
        bandera_confianza="baja",
        rango_inferior_kwh=80.0,
        rango_superior_kwh=120.0,
    )


async def test_upsert_y_get_devuelve_la_proyeccion_guardada() -> None:
    repo = FakeProyeccionRepository()
    proy = _make_proyeccion()
    await repo.upsert_proyeccion(proy)

    result = await repo.get_proyeccion("S1", date(2026, 6, 1))
    assert result == proy


async def test_get_devuelve_none_si_no_existe() -> None:
    repo = FakeProyeccionRepository()

    result = await repo.get_proyeccion("S1", date(2026, 6, 1))
    assert result is None


async def test_upsert_sobreescribe_proyeccion_existente() -> None:
    repo = FakeProyeccionRepository()
    proy_original = _make_proyeccion()
    await repo.upsert_proyeccion(proy_original)

    proy_nueva = ProyeccionMensual(
        suministro_id="S1",
        mes=date(2026, 6, 1),
        metodo_aplicado="interanual",
        meses_usados_como_base=12,
        dias_usados_como_base=17,
        bandera_confianza="alta",
        rango_inferior_kwh=90.0,
        rango_superior_kwh=110.0,
    )
    await repo.upsert_proyeccion(proy_nueva)

    result = await repo.get_proyeccion("S1", date(2026, 6, 1))
    assert result == proy_nueva
    assert result != proy_original


async def test_aislado_por_suministro_y_mes() -> None:
    repo = FakeProyeccionRepository()
    proy_s1 = _make_proyeccion("S1", date(2026, 6, 1))
    proy_s2 = _make_proyeccion("S2", date(2026, 6, 1))
    proy_julio = _make_proyeccion("S1", date(2026, 7, 1))

    await repo.upsert_proyeccion(proy_s1)
    await repo.upsert_proyeccion(proy_s2)
    await repo.upsert_proyeccion(proy_julio)

    assert await repo.get_proyeccion("S1", date(2026, 6, 1)) == proy_s1
    assert await repo.get_proyeccion("S2", date(2026, 6, 1)) == proy_s2
    assert await repo.get_proyeccion("S1", date(2026, 7, 1)) == proy_julio
