import asyncio
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, "src")

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.sqlite.models import Base, ConsumoDiario, Suministro

DB = "sqlite+aiosqlite:///./data/plataforma_clientes.db"


async def seed() -> None:
    engine = create_async_engine(DB, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        suministros = [
            Suministro(
                id="SRV-91013496", lat=-31.4200, lon=-64.1800, suministro_referencia="91013496"
            ),
            Suministro(
                id="SRV-91013500", lat=-31.4193, lon=-64.1800, suministro_referencia="91013500"
            ),
            Suministro(
                id="SRV-91013501", lat=-31.4200, lon=-64.1793, suministro_referencia="91013501"
            ),
            Suministro(
                id="SRV-91013502", lat=-31.4207, lon=-64.1800, suministro_referencia="91013502"
            ),
        ]
        for s in suministros:
            await session.merge(s)
        await session.flush()

        hoy = date(2026, 6, 17)
        random.seed(42)
        dia = date(2025, 1, 1)
        while dia <= hoy:
            mes = dia.month
            base = 15.0 if mes in (6, 7, 8) else 8.0 if mes in (12, 1, 2) else 11.0
            kwh = round(base + random.uniform(-1.5, 1.5), 2)
            stmt = (
                sqlite_insert(ConsumoDiario)
                .values(suministro_id="SRV-91013496", fecha=dia, kwh=kwh)
                .on_conflict_do_update(index_elements=["suministro_id", "fecha"], set_={"kwh": kwh})
            )
            await session.execute(stmt)
            dia += timedelta(days=1)

        for vecino_id, factor in [
            ("SRV-91013500", 0.9),
            ("SRV-91013501", 1.1),
            ("SRV-91013502", 0.95),
        ]:
            dia = date(2026, 5, 1)
            while dia <= hoy:
                mes = dia.month
                base = 15.0 if mes in (6, 7, 8) else 8.0 if mes in (12, 1, 2) else 11.0
                kwh = round((base + random.uniform(-1.0, 1.0)) * factor, 2)
                stmt = (
                    sqlite_insert(ConsumoDiario)
                    .values(suministro_id=vecino_id, fecha=dia, kwh=kwh)
                    .on_conflict_do_update(
                        index_elements=["suministro_id", "fecha"], set_={"kwh": kwh}
                    )
                )
                await session.execute(stmt)
                dia += timedelta(days=1)

        await session.commit()
    await engine.dispose()
    print("Datos de demo cargados OK")


asyncio.run(seed())
