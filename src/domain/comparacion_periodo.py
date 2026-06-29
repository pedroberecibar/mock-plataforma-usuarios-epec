"""Comparación de consumo a igual período.

El mes en curso se compara contra otro mes usando la **misma cantidad de
días**, pero matcheando por **día calendario** (no por conteo de filas): se
toman los días-del-mes presentes en la serie actual y se suman esos mismos
días en la serie de comparación. Así un hueco en la serie no desalinea las
ventanas (defecto del antiguo `min(len(serie), días_del_mes)`).
"""

from datetime import date

Serie = list[tuple[date, float]]


def dias_con_dato(serie: Serie) -> set[int]:
    """Días-del-mes (1..31) presentes en la serie."""
    return {fecha.day for fecha, _ in serie}


def total_en_dias(serie: Serie, dias: set[int]) -> float:
    """Suma de la serie restringida a los días-del-mes indicados."""
    return sum(kwh for fecha, kwh in serie if fecha.day in dias)


def variacion_pct(actual: float | None, base: float) -> float | None:
    """Variación porcentual de `actual` respecto de `base`.

    Devuelve None si no hay dato actual o la base no es positiva
    (evita divisiones por cero y porcentajes sin sentido).
    """
    if actual is None or base <= 0:
        return None
    return round((actual - base) / base * 100, 2)
