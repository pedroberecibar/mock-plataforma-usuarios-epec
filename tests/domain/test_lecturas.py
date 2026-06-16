from datetime import date

from domain.lecturas import LecturaTelemedida


def test_lectura_telemedida_es_inmutable() -> None:
    lectura = LecturaTelemedida(
        equipo="91013496",
        cdr_codigo="E",
        fecha=date(2026, 6, 1),
        valor_kwh=1234.56,
    )

    assert lectura.equipo == "91013496"
    assert lectura.cdr_codigo == "E"
    assert lectura.fecha == date(2026, 6, 1)
    assert lectura.valor_kwh == 1234.56


def test_lecturas_iguales_si_mismos_campos() -> None:
    a = LecturaTelemedida("91013496", "E", date(2026, 6, 1), 100.0)
    b = LecturaTelemedida("91013496", "E", date(2026, 6, 1), 100.0)
    assert a == b


def test_lecturas_distintas_si_difiere_algun_campo() -> None:
    a = LecturaTelemedida("91013496", "E", date(2026, 6, 1), 100.0)
    b = LecturaTelemedida("91013496", "E", date(2026, 6, 2), 100.0)
    assert a != b
