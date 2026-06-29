"""Tests para PoblarSuministroUseCase — sin I/O real (fakes + in-memory SQLite)."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.lecturas import LecturaTelemedida
from domain.ports.suministro_ingestion_strategy import SuministroIngestionStrategy
from infrastructure.fakes.vecinos_repository import FakeVecinosRepository
from infrastructure.oracle.ingestion_strategy_selector import IngestionStrategySelector
from infrastructure.oracle.suministro_meta_reader import SuministroMeta
from infrastructure.orchestration.poblar_suministro import PoblarSuministroUseCase

# ---------------------------------------------------------------------------
# Helpers / fakes locales
# ---------------------------------------------------------------------------


class _FakeStrategy(SuministroIngestionStrategy):
    def __init__(self, lecturas: list[LecturaTelemedida], nombre: str = "FAKE") -> None:
        self._lecturas = lecturas
        self._nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def soporta_perfiles(self) -> bool:
        return False

    async def leer_lecturas(
        self, medidor: str, srv_codigo: str, desde: date, hasta: date
    ) -> list[LecturaTelemedida]:
        return self._lecturas


def _make_selector(strategy: SuministroIngestionStrategy) -> IngestionStrategySelector:
    class _FakeClou(SuministroIngestionStrategy):
        @property
        def nombre(self) -> str:
            return "CLOU"

        @property
        def soporta_perfiles(self) -> bool:
            return True

        async def leer_lecturas(self, m: str, s: str, d: date, h: date) -> list[LecturaTelemedida]:
            return []

    clou = _FakeClou()
    return IngestionStrategySelector(clou=clou, nansen=clou, chupete=strategy)  # type: ignore[arg-type]


def _meta(
    medidor: str = "99000001",
    telemedible: str | None = None,
    lat: float = -31.4,
    lon: float = -64.2,
    tarifa: str = "140",
) -> SuministroMeta:
    return SuministroMeta(
        medidor=medidor,
        telemedible=telemedible,
        lat=lat,
        lon=lon,
        subestacion="4694",
        codigo_tarifa=tarifa,
    )


def _lectura(
    equipo: str = "99000001",
    fecha: date = date(2026, 1, 1),
    valor: float = 1000.0,
    srv: str = "SRV-TEST",
) -> LecturaTelemedida:
    return LecturaTelemedida(
        equipo=equipo,
        srv_codigo=srv,
        cdr_codigo="E",
        fecha=fecha,
        valor_kwh=valor,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_poblar_sin_oracle_disponible_abort(db_session_factory: object) -> None:
    """Si meta_reader retorna None (Oracle inaccesible), el use case termina sin error."""
    meta_reader = MagicMock()
    meta_reader.leer_meta = AsyncMock(return_value=None)

    uc = PoblarSuministroUseCase(
        meta_reader=meta_reader,
        selector=_make_selector(_FakeStrategy([])),
        vecinos_repo=FakeVecinosRepository(),
        session_factory=db_session_factory,  # type: ignore[arg-type]
    )
    await uc.ejecutar("SRV-999")  # no debe lanzar


@pytest.mark.asyncio
async def test_poblar_sin_medidor_no_ingesta(db_session_factory: object) -> None:
    """Si la metadata no tiene medidor, el use case no ingesta lecturas."""
    meta_reader = MagicMock()
    meta_reader.leer_meta = AsyncMock(
        return_value=SuministroMeta(
            medidor=None,
            telemedible=None,
            lat=-31.4,
            lon=-64.2,
            subestacion=None,
            codigo_tarifa=None,
        )
    )
    strategy = _FakeStrategy([_lectura()])
    strategy.leer_lecturas = AsyncMock(return_value=[])  # type: ignore[method-assign]

    uc = PoblarSuministroUseCase(
        meta_reader=meta_reader,
        selector=_make_selector(strategy),
        vecinos_repo=FakeVecinosRepository(),
        session_factory=db_session_factory,  # type: ignore[arg-type]
    )
    await uc.ejecutar("SRV-TEST")
    strategy.leer_lecturas.assert_not_called()


@pytest.mark.asyncio
async def test_poblar_con_lecturas_persiste_consumo(db_session_factory: object) -> None:
    """Con lecturas disponibles, se persiste consumo_diario en SQLite."""
    from sqlalchemy import text

    meta_reader = MagicMock()
    meta_reader.leer_meta = AsyncMock(return_value=_meta(medidor="99000001"))

    d0 = date(2026, 1, 1)
    d1 = date(2026, 1, 6)
    lecturas = [_lectura("99000001", d0, 1000.0), _lectura("99000001", d1, 1050.0)]
    strategy = _FakeStrategy(lecturas, nombre="CHUPETE")

    uc = PoblarSuministroUseCase(
        meta_reader=meta_reader,
        selector=_make_selector(strategy),
        vecinos_repo=FakeVecinosRepository({"SRV-TEST": ["SRV-200"]}),
        session_factory=db_session_factory,  # type: ignore[arg-type]
    )
    await uc.ejecutar("SRV-TEST")

    async with db_session_factory() as session:  # type: ignore[attr-defined]
        result = await session.execute(
            text("SELECT COUNT(*) FROM consumo_diario WHERE suministro_id = 'SRV-TEST'")
        )
        count = result.scalar()
    assert count == 5  # 5 días entre d0 y d1
