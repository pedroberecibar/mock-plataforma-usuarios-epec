"""TDD tests para ObtenerComparacionHistoricaUseCase.

Semántica de datos faltantes: cada período devuelve lista vacía cuando
no hay datos — el frontend detecta ausencia por len(serie)==0.
total_kwh es None cuando la serie está vacía.
"""

from datetime import date

from application.use_cases.obtener_comparacion_historica import (
    ObtenerComparacionHistoricaUseCase,
)
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.vecinos_repository import FakeVecinosRepository


async def _repo_con_junio_2026() -> FakeConsumoDiarioRepository:
    repo = FakeConsumoDiarioRepository()
    # Mes actual: junio 2026
    for dia in range(1, 16):
        await repo.upsert_consumo("S1", date(2026, 6, dia), 10.0)
    # Mes anterior: mayo 2026
    for dia in range(1, 32):
        await repo.upsert_consumo("S1", date(2026, 5, dia), 8.0)
    # Mismo mes año anterior: junio 2025
    for dia in range(1, 31):
        await repo.upsert_consumo("S1", date(2025, 6, dia), 12.0)
    return repo


async def test_devuelve_tres_periodos() -> None:
    repo = await _repo_con_junio_2026()
    uc = ObtenerComparacionHistoricaUseCase(repo)

    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.mes_actual.mes == date(2026, 6, 1)
    assert resultado.mes_anterior.mes == date(2026, 5, 1)
    assert resultado.mismo_mes_anio_anterior.mes == date(2025, 6, 1)


async def test_total_kwh_suma_correctamente() -> None:
    repo = await _repo_con_junio_2026()
    uc = ObtenerComparacionHistoricaUseCase(repo)

    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    # 15 días × 10 kWh = 150 kWh en junio 2026
    assert resultado.mes_actual.total_kwh == 150.0
    # 31 días × 8 kWh = 248 kWh en mayo 2026
    assert resultado.mes_anterior.total_kwh == 248.0
    # 30 días × 12 kWh = 360 kWh en junio 2025
    assert resultado.mismo_mes_anio_anterior.total_kwh == 360.0


async def test_variacion_pct_vs_mes_completo() -> None:
    """El % compara el acumulado del mes en curso contra el TOTAL del mes/año
    de comparación completo (no a igual período)."""
    repo = await _repo_con_junio_2026()
    uc = ObtenerComparacionHistoricaUseCase(repo)

    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    # Junio 1-15 = 150. Mayo completo = 31×8 = 248 → (150-248)/248 = -39.52%.
    assert resultado.vs_mes_anterior_pct == -39.52
    # Junio 2025 completo = 30×12 = 360 → (150-360)/360 = -58.33%.
    assert resultado.vs_anio_anterior_pct == -58.33


async def test_variacion_pct_none_sin_datos_de_comparacion() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.vs_mes_anterior_pct is None
    assert resultado.vs_anio_anterior_pct is None


async def test_periodo_sin_datos_devuelve_lista_vacia_y_total_none() -> None:
    repo = FakeConsumoDiarioRepository()
    # Solo tiene datos en mes actual
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.mes_actual.serie != []
    assert resultado.mes_anterior.serie == []
    assert resultado.mes_anterior.total_kwh is None
    assert resultado.mismo_mes_anio_anterior.serie == []
    assert resultado.mismo_mes_anio_anterior.total_kwh is None


async def test_datos_hasta_refleja_ultima_fecha_global() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 15), 10.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.datos_hasta == date(2026, 6, 15)


async def test_mes_parametro_normalizado_a_primer_dia() -> None:
    """Aceptar cualquier día del mes — normaliza al primer día."""
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 5), 10.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    # Se pasa el 15 del mes, debe tratarse como si fuera el 1
    resultado_15 = await uc.ejecutar("S1", mes=date(2026, 6, 15))
    resultado_1 = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado_15.mes_actual.mes == resultado_1.mes_actual.mes


async def test_aislado_por_suministro() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)
    await repo.upsert_consumo("S2", date(2026, 6, 1), 99.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert all(kwh != 99.0 for _, kwh in resultado.mes_actual.serie)


async def test_zona_sin_vecinos_devuelve_n_vecinos_cero() -> None:
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)
    vecinos_repo = FakeVecinosRepository({})

    uc = ObtenerComparacionHistoricaUseCase(repo, vecinos_repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.zona_mes_actual.n_vecinos == 0
    assert resultado.zona_mes_actual.promedio_vecinos_kwh is None
    assert resultado.zona_mes_actual.diferencia_pct is None


async def test_zona_con_vecinos_suficientes_calcula_diferencia() -> None:
    repo = FakeConsumoDiarioRepository()
    # Suministro principal: 100 kWh en junio 2026
    for d in range(1, 11):
        await repo.upsert_consumo("S1", date(2026, 6, d), 10.0)
    # 6 vecinos con 80 kWh cada uno → promedio 80
    for i in range(1, 7):
        for d in range(1, 11):
            await repo.upsert_consumo(f"V{i}", date(2026, 6, d), 8.0)
    vecinos_repo = FakeVecinosRepository({"S1": [f"V{i}" for i in range(1, 7)]})

    uc = ObtenerComparacionHistoricaUseCase(repo, vecinos_repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.zona_mes_actual.n_vecinos == 6
    assert resultado.zona_mes_actual.promedio_vecinos_kwh == 80.0
    # 100 vs 80 → +25%
    assert resultado.zona_mes_actual.diferencia_pct == 25.0


async def test_zona_sin_vecinos_repo_devuelve_zona_vacia() -> None:
    """Sin vecinos_repo inyectado, zona_mes_actual retorna n_vecinos=0."""
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)

    uc = ObtenerComparacionHistoricaUseCase(repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.zona_mes_actual.n_vecinos == 0
    assert resultado.zona_mes_actual.promedio_vecinos_kwh is None


async def test_zona_serie_diaria_promedio_correcto() -> None:
    """serie de zona contiene el promedio de vecinos por cada día."""
    repo = FakeConsumoDiarioRepository()
    for d in range(1, 6):
        await repo.upsert_consumo("S1", date(2026, 6, d), 10.0)
    # 6 vecinos: los 3 primeros consumen 6 kWh/día, los 3 últimos 12 kWh/día → promedio 9 kWh/día
    for i in range(1, 4):
        for d in range(1, 6):
            await repo.upsert_consumo(f"V{i}", date(2026, 6, d), 6.0)
    for i in range(4, 7):
        for d in range(1, 6):
            await repo.upsert_consumo(f"V{i}", date(2026, 6, d), 12.0)
    vecinos_repo = FakeVecinosRepository({"S1": [f"V{i}" for i in range(1, 7)]})

    uc = ObtenerComparacionHistoricaUseCase(repo, vecinos_repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    zona = resultado.zona_mes_actual
    assert len(zona.serie) == 5
    assert all(abs(kwh - 9.0) < 0.01 for _, kwh in zona.serie)
    assert zona.serie[0][0] == date(2026, 6, 1)


async def test_zona_serie_vacia_cuando_menos_de_cinco_vecinos() -> None:
    """Con menos de 5 vecinos la serie de zona queda vacía (privacidad)."""
    repo = FakeConsumoDiarioRepository()
    await repo.upsert_consumo("S1", date(2026, 6, 1), 10.0)
    for i in range(1, 4):
        await repo.upsert_consumo(f"V{i}", date(2026, 6, 1), 8.0)
    vecinos_repo = FakeVecinosRepository({"S1": [f"V{i}" for i in range(1, 4)]})

    uc = ObtenerComparacionHistoricaUseCase(repo, vecinos_repo)
    resultado = await uc.ejecutar("S1", mes=date(2026, 6, 1))

    assert resultado.zona_mes_actual.serie == []
