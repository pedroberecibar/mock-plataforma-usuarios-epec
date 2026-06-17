"""Tests de integración para SQLiteVecinosRepository (bounding box + Haversine)."""

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.sqlite.models import Suministro
from infrastructure.sqlite.vecinos_repository import SQLiteVecinosRepository

# Coordenadas de referencia: Córdoba capital, Argentina
_LAT_REF = -31.4200
_LON_REF = -64.1800

# ~100 m al norte (≈ 0.0009° de latitud)
_LAT_CERCA = -31.4191
_LON_CERCA = -64.1800

# ~200 m al norte (demasiado lejos para radio 150 m)
_LAT_LEJOS = -31.4182
_LON_LEJOS = -64.1800


async def _add_suministro(session: AsyncSession, sid: str, lat: float, lon: float) -> None:
    session.add(Suministro(id=sid, lat=lat, lon=lon, suministro_referencia=sid))
    await session.flush()


async def test_vecino_dentro_del_radio_es_incluido(db_session: AsyncSession) -> None:
    await _add_suministro(db_session, "S-REF", _LAT_REF, _LON_REF)
    await _add_suministro(db_session, "S-CERCA", _LAT_CERCA, _LON_CERCA)

    repo = SQLiteVecinosRepository(db_session)
    vecinos = await repo.get_vecinos("S-REF", 150.0)

    assert "S-CERCA" in vecinos


async def test_vecino_fuera_del_radio_es_excluido(db_session: AsyncSession) -> None:
    await _add_suministro(db_session, "S-REF", _LAT_REF, _LON_REF)
    await _add_suministro(db_session, "S-LEJOS", _LAT_LEJOS, _LON_LEJOS)

    repo = SQLiteVecinosRepository(db_session)
    vecinos = await repo.get_vecinos("S-REF", 150.0)

    assert "S-LEJOS" not in vecinos


async def test_propio_suministro_no_aparece_en_resultado(db_session: AsyncSession) -> None:
    await _add_suministro(db_session, "S-REF", _LAT_REF, _LON_REF)

    repo = SQLiteVecinosRepository(db_session)
    vecinos = await repo.get_vecinos("S-REF", 150.0)

    assert "S-REF" not in vecinos


async def test_retorna_lista_vacia_si_no_hay_vecinos(db_session: AsyncSession) -> None:
    await _add_suministro(db_session, "S-REF", _LAT_REF, _LON_REF)
    await _add_suministro(db_session, "S-LEJOS", _LAT_LEJOS, _LON_LEJOS)

    repo = SQLiteVecinosRepository(db_session)
    vecinos = await repo.get_vecinos("S-REF", 150.0)

    assert vecinos == []


async def test_retorna_lista_vacia_si_suministro_no_existe(db_session: AsyncSession) -> None:
    repo = SQLiteVecinosRepository(db_session)
    vecinos = await repo.get_vecinos("S-NO-EXISTE", 150.0)

    assert vecinos == []


async def test_incluye_multiples_vecinos_en_rango(db_session: AsyncSession) -> None:
    await _add_suministro(db_session, "S-REF", _LAT_REF, _LON_REF)
    await _add_suministro(db_session, "S-V1", _LAT_CERCA, _LON_CERCA)
    # Vecino 2: ~80 m al este
    await _add_suministro(db_session, "S-V2", _LAT_REF, -64.1793)
    await _add_suministro(db_session, "S-LEJOS", _LAT_LEJOS, _LON_LEJOS)

    repo = SQLiteVecinosRepository(db_session)
    vecinos = await repo.get_vecinos("S-REF", 150.0)

    assert "S-V1" in vecinos
    assert "S-V2" in vecinos
    assert "S-LEJOS" not in vecinos
    assert len(vecinos) == 2
