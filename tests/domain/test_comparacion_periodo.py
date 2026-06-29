"""TDD tests para el helper de comparación a igual período.

Política: comparar el mes en curso contra la misma cantidad de días
*matcheando por día calendario* (no por conteo de filas), de modo que
los huecos en la serie no desalineen las ventanas.
"""

from datetime import date

from domain.comparacion_periodo import (
    dias_con_dato,
    total_en_dias,
    variacion_pct,
)


def test_dias_con_dato_devuelve_dias_del_mes() -> None:
    serie = [(date(2026, 6, 1), 10.0), (date(2026, 6, 3), 12.0)]
    assert dias_con_dato(serie) == {1, 3}


def test_total_en_dias_suma_solo_los_dias_pedidos() -> None:
    serie = [
        (date(2026, 5, 1), 8.0),
        (date(2026, 5, 2), 9.0),
        (date(2026, 5, 3), 7.0),
    ]
    assert total_en_dias(serie, {1, 3}) == 15.0


def test_total_en_dias_ignora_dias_inexistentes_en_la_comparacion() -> None:
    # El mes en curso llegó al día 31, pero la comparación (abril) no tiene día 31.
    serie_abril = [(date(2026, 4, d), 5.0) for d in range(1, 31)]
    # Solo deben sumar los días 1..30 presentes; el 31 no existe en abril.
    assert total_en_dias(serie_abril, {1, 30, 31}) == 10.0


def test_total_en_dias_matchea_por_dia_calendario_con_huecos() -> None:
    # Mes en curso con hueco: días {1, 2, 27} (faltan 3..26).
    dias_actuales = {1, 2, 27}
    serie_anterior = [(date(2026, 5, d), 4.0) for d in range(1, 32)]
    # Debe sumar SOLO los días 1, 2 y 27 → 3 × 4 = 12, no los primeros 3 días.
    assert total_en_dias(serie_anterior, dias_actuales) == 12.0


def test_variacion_pct_positiva() -> None:
    assert variacion_pct(150.0, 100.0) == 50.0


def test_variacion_pct_negativa() -> None:
    assert variacion_pct(80.0, 100.0) == -20.0


def test_variacion_pct_none_si_base_no_positiva() -> None:
    assert variacion_pct(100.0, 0.0) is None
    assert variacion_pct(100.0, -5.0) is None


def test_variacion_pct_none_si_actual_es_none() -> None:
    assert variacion_pct(None, 100.0) is None
