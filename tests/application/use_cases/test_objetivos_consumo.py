from datetime import date

import pytest

from application.use_cases.get_objetivo_consumo import GetObjetivoConsumoUseCase
from application.use_cases.set_objetivo_consumo import SetObjetivoConsumoUseCase
from infrastructure.fakes.objetivo_consumo_repository import FakeObjetivoConsumoRepository


@pytest.fixture
def repo() -> FakeObjetivoConsumoRepository:
    return FakeObjetivoConsumoRepository()


# ---------------------------------------------------------------------------
# SetObjetivoConsumoUseCase
# ---------------------------------------------------------------------------


async def test_set_objetivo_persiste_el_valor(repo: FakeObjetivoConsumoRepository) -> None:
    uc = SetObjetivoConsumoUseCase(repo)
    await uc.ejecutar("3037481", 120.0)

    resultado = await repo.get_vigente("3037481")
    assert resultado is not None
    valor, origen, _ = resultado
    assert valor == 120.0
    assert origen == "manual"


async def test_set_objetivo_usa_fecha_de_hoy(repo: FakeObjetivoConsumoRepository) -> None:
    uc = SetObjetivoConsumoUseCase(repo)
    hoy = date.today()
    await uc.ejecutar("3037481", 80.0)

    resultado = await repo.get_vigente("3037481")
    assert resultado is not None
    _, _, vigente_desde = resultado
    assert vigente_desde == hoy


async def test_set_objetivo_rechaza_kwh_no_positivo(repo: FakeObjetivoConsumoRepository) -> None:
    uc = SetObjetivoConsumoUseCase(repo)
    with pytest.raises(ValueError, match="positivo"):
        await uc.ejecutar("3037481", 0.0)


# ---------------------------------------------------------------------------
# GetObjetivoConsumoUseCase
# ---------------------------------------------------------------------------


async def test_get_objetivo_devuelve_none_cuando_no_hay_objetivo(
    repo: FakeObjetivoConsumoRepository,
) -> None:
    uc = GetObjetivoConsumoUseCase(repo)
    resultado = await uc.ejecutar("3037481")
    assert resultado is None


async def test_get_objetivo_devuelve_el_vigente(repo: FakeObjetivoConsumoRepository) -> None:
    await repo.upsert_objetivo("3037481", 150.0, "manual", date(2026, 6, 1))
    uc = GetObjetivoConsumoUseCase(repo)

    resultado = await uc.ejecutar("3037481")

    assert resultado is not None
    assert resultado["valor_kwh"] == 150.0
    assert resultado["origen"] == "manual"
    assert resultado["vigente_desde"] == date(2026, 6, 1)


async def test_get_objetivo_devuelve_el_mas_reciente(
    repo: FakeObjetivoConsumoRepository,
) -> None:
    await repo.upsert_objetivo("3037481", 100.0, "manual", date(2026, 1, 1))
    await repo.upsert_objetivo("3037481", 200.0, "manual", date(2026, 6, 1))
    uc = GetObjetivoConsumoUseCase(repo)

    resultado = await uc.ejecutar("3037481")

    assert resultado is not None
    assert resultado["valor_kwh"] == 200.0
