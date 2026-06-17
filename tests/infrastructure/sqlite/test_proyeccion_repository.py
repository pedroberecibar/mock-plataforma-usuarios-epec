"""Tests de integración para SQLiteProyeccionRepository."""

from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domain.proyeccion import ProyeccionMensual
from infrastructure.sqlite.proyeccion_repository import SQLiteProyeccionRepository


def _make_proyeccion(
    suministro_id: str, mes: date, metodo: str = "reciente", confianza: str = "baja"
) -> ProyeccionMensual:
    return ProyeccionMensual(
        suministro_id=suministro_id,
        mes=mes,
        metodo_aplicado=metodo,
        meses_usados_como_base=0,
        dias_usados_como_base=7,
        bandera_confianza=confianza,
        rango_inferior_kwh=80.0,
        rango_superior_kwh=120.0,
    )


async def test_get_proyeccion_devuelve_none_si_no_existe(
    db_session: AsyncSession, suministro_fixture: str
) -> None:
    repo = SQLiteProyeccionRepository(db_session)
    result = await repo.get_proyeccion(suministro_fixture, date(2026, 6, 1))
    assert result is None


async def test_upsert_y_get_devuelve_proyeccion(
    db_session: AsyncSession, suministro_fixture: str
) -> None:
    repo = SQLiteProyeccionRepository(db_session)
    proy = _make_proyeccion(suministro_fixture, date(2026, 6, 1))

    await repo.upsert_proyeccion(proy)
    result = await repo.get_proyeccion(suministro_fixture, date(2026, 6, 1))

    assert result is not None
    assert result.suministro_id == suministro_fixture
    assert result.mes == date(2026, 6, 1)
    assert result.metodo_aplicado == "reciente"
    assert result.bandera_confianza == "baja"
    assert result.rango_inferior_kwh == pytest.approx(80.0)
    assert result.rango_superior_kwh == pytest.approx(120.0)


async def test_upsert_sobreescribe_proyeccion_existente(
    db_session: AsyncSession, suministro_fixture: str
) -> None:
    repo = SQLiteProyeccionRepository(db_session)
    proy_original = _make_proyeccion(suministro_fixture, date(2026, 6, 1))
    await repo.upsert_proyeccion(proy_original)

    proy_nueva = ProyeccionMensual(
        suministro_id=suministro_fixture,
        mes=date(2026, 6, 1),
        metodo_aplicado="interanual",
        meses_usados_como_base=12,
        dias_usados_como_base=17,
        bandera_confianza="alta",
        rango_inferior_kwh=90.0,
        rango_superior_kwh=110.0,
    )
    await repo.upsert_proyeccion(proy_nueva)
    result = await repo.get_proyeccion(suministro_fixture, date(2026, 6, 1))

    assert result is not None
    assert result.metodo_aplicado == "interanual"
    assert result.bandera_confianza == "alta"


async def test_proyeccion_insuficiente_acepta_rangos_none(
    db_session: AsyncSession, suministro_fixture: str
) -> None:
    repo = SQLiteProyeccionRepository(db_session)
    proy = ProyeccionMensual(
        suministro_id=suministro_fixture,
        mes=date(2026, 6, 1),
        metodo_aplicado="insuficiente",
        meses_usados_como_base=0,
        dias_usados_como_base=3,
        bandera_confianza="sin_datos",
        rango_inferior_kwh=None,
        rango_superior_kwh=None,
    )
    await repo.upsert_proyeccion(proy)
    result = await repo.get_proyeccion(suministro_fixture, date(2026, 6, 1))

    assert result is not None
    assert result.rango_inferior_kwh is None
    assert result.rango_superior_kwh is None
