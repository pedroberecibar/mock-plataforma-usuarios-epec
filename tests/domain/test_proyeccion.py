"""Tests para el dataclass de dominio ProyeccionMensual."""

from datetime import date

from domain.proyeccion import ProyeccionMensual


def test_se_puede_instanciar_con_todos_los_campos() -> None:
    proy = ProyeccionMensual(
        suministro_id="S1",
        mes=date(2026, 6, 1),
        metodo_aplicado="reciente",
        meses_usados_como_base=0,
        dias_usados_como_base=7,
        bandera_confianza="baja",
        rango_inferior_kwh=80.0,
        rango_superior_kwh=120.0,
    )
    assert proy.suministro_id == "S1"
    assert proy.mes == date(2026, 6, 1)
    assert proy.rango_inferior_kwh == 80.0


def test_rangos_pueden_ser_none_para_metodo_insuficiente() -> None:
    proy = ProyeccionMensual(
        suministro_id="S1",
        mes=date(2026, 6, 1),
        metodo_aplicado="insuficiente",
        meses_usados_como_base=0,
        dias_usados_como_base=3,
        bandera_confianza="sin_datos",
        rango_inferior_kwh=None,
        rango_superior_kwh=None,
    )
    assert proy.rango_inferior_kwh is None
    assert proy.rango_superior_kwh is None


def test_es_frozen_e_inmutable() -> None:
    import dataclasses

    import pytest

    proy = ProyeccionMensual(
        suministro_id="S1",
        mes=date(2026, 6, 1),
        metodo_aplicado="reciente",
        meses_usados_como_base=0,
        dias_usados_como_base=7,
        bandera_confianza="baja",
        rango_inferior_kwh=80.0,
        rango_superior_kwh=120.0,
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        proy.suministro_id = "S2"  # type: ignore[misc]
