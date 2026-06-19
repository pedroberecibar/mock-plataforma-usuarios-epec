"""TDD tests para ObtenerHomeUseCase."""

from datetime import date

from application.use_cases.calcular_proyeccion_mensual import CalcularProyeccionMensualUseCase
from application.use_cases.obtener_home import ObtenerHomeUseCase
from domain.proyeccion import ProyeccionMensual
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.proyeccion_repository import FakeProyeccionRepository
from infrastructure.fakes.vecinos_repository import FakeVecinosRepository


def _make_uc(
    consumo: FakeConsumoDiarioRepository,
    vecinos: FakeVecinosRepository,
    proy_repo: FakeProyeccionRepository,
) -> ObtenerHomeUseCase:
    calcular_uc = CalcularProyeccionMensualUseCase(consumo, proy_repo)
    return ObtenerHomeUseCase(consumo, vecinos, proy_repo, calcular_uc)


async def _seed_mes(
    repo: FakeConsumoDiarioRepository,
    suministro_id: str,
    year: int,
    month: int,
    kwh_por_dia: float,
    dias: int,
) -> None:
    for dia in range(1, dias + 1):
        await repo.upsert_consumo(suministro_id, date(year, month, dia), kwh_por_dia)


# ---------------------------------------------------------------------------
# consumo_mes
# ---------------------------------------------------------------------------


async def test_total_kwh_suma_datos_del_mes_actual() -> None:
    consumo = FakeConsumoDiarioRepository()
    await consumo.upsert_consumo("S1", date(2026, 6, 1), 10.0)
    await consumo.upsert_consumo("S1", date(2026, 6, 2), 12.0)

    uc = _make_uc(consumo, FakeVecinosRepository(), FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.consumo_mes.total_kwh == 22.0


async def test_total_kwh_es_none_si_no_hay_datos_en_el_mes() -> None:
    consumo = FakeConsumoDiarioRepository()

    uc = _make_uc(consumo, FakeVecinosRepository(), FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.consumo_mes.total_kwh is None


async def test_vs_mes_anterior_negativo_si_consumo_bajo() -> None:
    consumo = FakeConsumoDiarioRepository()
    # Mayo: 100 kWh en los primeros 10 días
    await _seed_mes(consumo, "S1", 2026, 5, 10.0, 10)
    # Junio: 50 kWh en los primeros 10 días (bajó)
    await _seed_mes(consumo, "S1", 2026, 6, 5.0, 10)

    uc = _make_uc(consumo, FakeVecinosRepository(), FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.consumo_mes.vs_mes_anterior_pct is not None
    assert result.consumo_mes.vs_mes_anterior_pct < 0


async def test_vs_mes_anterior_positivo_si_consumo_subio() -> None:
    consumo = FakeConsumoDiarioRepository()
    await _seed_mes(consumo, "S1", 2026, 5, 5.0, 10)
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 10)

    uc = _make_uc(consumo, FakeVecinosRepository(), FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.consumo_mes.vs_mes_anterior_pct is not None
    assert result.consumo_mes.vs_mes_anterior_pct > 0


async def test_vs_anio_anterior_compara_mismo_periodo() -> None:
    consumo = FakeConsumoDiarioRepository()
    await _seed_mes(consumo, "S1", 2025, 6, 10.0, 10)  # 100 kWh año anterior
    await _seed_mes(consumo, "S1", 2026, 6, 15.0, 10)  # 150 kWh este año (+50%)

    uc = _make_uc(consumo, FakeVecinosRepository(), FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.consumo_mes.vs_anio_anterior_pct is not None
    assert abs(result.consumo_mes.vs_anio_anterior_pct - 50.0) < 1.0


# ---------------------------------------------------------------------------
# comparacion_zona
# ---------------------------------------------------------------------------


async def test_comparacion_zona_sin_vecinos() -> None:
    consumo = FakeConsumoDiarioRepository()
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 10)
    vecinos = FakeVecinosRepository()  # sin vecinos configurados

    uc = _make_uc(consumo, vecinos, FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.comparacion_zona.n_vecinos == 0
    assert result.comparacion_zona.promedio_vecinos_kwh is None
    assert result.comparacion_zona.diferencia_pct is None


async def test_comparacion_zona_pocos_vecinos_sin_datos_privacidad() -> None:
    consumo = FakeConsumoDiarioRepository()
    await _seed_mes(consumo, "S1", 2026, 6, 20.0, 10)  # S1: 200 kWh
    await _seed_mes(consumo, "S2", 2026, 6, 10.0, 10)  # S2: 100 kWh
    await _seed_mes(consumo, "S3", 2026, 6, 10.0, 10)  # S3: 100 kWh
    vecinos = FakeVecinosRepository(vecinos={"S1": ["S2", "S3"]})  # solo 2 < 5

    uc = _make_uc(consumo, vecinos, FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    # Con n_vecinos < 5 no se expone el promedio (Ley 25.326 / CU-NF02)
    assert result.comparacion_zona.n_vecinos == 2
    assert result.comparacion_zona.promedio_vecinos_kwh is None
    assert result.comparacion_zona.diferencia_pct is None


async def test_comparacion_zona_con_suficientes_vecinos() -> None:
    consumo = FakeConsumoDiarioRepository()
    await _seed_mes(consumo, "S1", 2026, 6, 20.0, 10)  # S1: 200 kWh
    for i in range(2, 7):
        await _seed_mes(consumo, f"S{i}", 2026, 6, 10.0, 10)  # S2-S6: 100 kWh cada uno
    vecinos = FakeVecinosRepository(vecinos={"S1": [f"S{i}" for i in range(2, 7)]})

    uc = _make_uc(consumo, vecinos, FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.comparacion_zona.n_vecinos == 5
    assert result.comparacion_zona.promedio_vecinos_kwh == 100.0
    assert result.comparacion_zona.diferencia_pct is not None
    assert abs(result.comparacion_zona.diferencia_pct - 100.0) < 0.01


# ---------------------------------------------------------------------------
# proyeccion
# ---------------------------------------------------------------------------


async def test_proyeccion_usa_cache_si_existe() -> None:
    consumo = FakeConsumoDiarioRepository()
    proy_repo = FakeProyeccionRepository()
    cache = ProyeccionMensual(
        suministro_id="S1",
        mes=date(2026, 6, 1),
        metodo_aplicado="interanual",
        meses_usados_como_base=12,
        dias_usados_como_base=17,
        bandera_confianza="alta",
        rango_inferior_kwh=90.0,
        rango_superior_kwh=110.0,
    )
    await proy_repo.upsert_proyeccion(cache)

    uc = _make_uc(consumo, FakeVecinosRepository(), proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.proyeccion.metodo_aplicado == "interanual"
    assert result.proyeccion.bandera_confianza == "alta"


async def test_proyeccion_calcula_si_no_hay_cache() -> None:
    consumo = FakeConsumoDiarioRepository()
    await _seed_mes(consumo, "S1", 2026, 6, 10.0, 10)
    proy_repo = FakeProyeccionRepository()

    uc = _make_uc(consumo, FakeVecinosRepository(), proy_repo)
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.proyeccion is not None
    assert result.proyeccion.metodo_aplicado in {
        "reciente",
        "interanual",
        "estacional",
        "insuficiente",
    }


# ---------------------------------------------------------------------------
# Metadatos
# ---------------------------------------------------------------------------


async def test_datos_hasta_refleja_ultima_fecha_con_dato() -> None:
    consumo = FakeConsumoDiarioRepository()
    await consumo.upsert_consumo("S1", date(2026, 6, 1), 10.0)
    await consumo.upsert_consumo("S1", date(2026, 6, 14), 9.0)

    uc = _make_uc(consumo, FakeVecinosRepository(), FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.datos_hasta == date(2026, 6, 14)


async def test_timestamp_es_utc() -> None:

    consumo = FakeConsumoDiarioRepository()

    uc = _make_uc(consumo, FakeVecinosRepository(), FakeProyeccionRepository())
    result = await uc.ejecutar("S1", date(2026, 6, 1))

    assert result.timestamp.tzinfo is not None
    assert result.timestamp.utcoffset() is not None
