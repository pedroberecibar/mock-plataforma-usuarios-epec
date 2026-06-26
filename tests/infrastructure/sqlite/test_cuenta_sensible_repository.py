from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.sqlite.cuenta_sensible_repository import SQLiteCuentaSensibleRepository


async def test_get_inexistente_devuelve_none(db_session: AsyncSession) -> None:
    repo = SQLiteCuentaSensibleRepository(db_session)
    assert await repo.get("SRV-2817670") is None


async def test_upsert_y_get(db_session: AsyncSession) -> None:
    repo = SQLiteCuentaSensibleRepository(db_session)
    await repo.upsert("SRV-2817670", nro_documento_enc="enc:24241815", cuit_enc="enc:27242418153")
    assert await repo.get("SRV-2817670") == ("enc:24241815", "enc:27242418153")


async def test_upsert_actualiza_existente(db_session: AsyncSession) -> None:
    repo = SQLiteCuentaSensibleRepository(db_session)
    await repo.upsert("SRV-1", nro_documento_enc="enc:A", cuit_enc=None)
    await repo.upsert("SRV-1", nro_documento_enc="enc:B", cuit_enc="enc:C")
    assert await repo.get("SRV-1") == ("enc:B", "enc:C")


async def test_upsert_solo_nro_deja_cuit_none(db_session: AsyncSession) -> None:
    repo = SQLiteCuentaSensibleRepository(db_session)
    await repo.upsert("SRV-9", nro_documento_enc="enc:24241815", cuit_enc=None)
    assert await repo.get("SRV-9") == ("enc:24241815", None)
