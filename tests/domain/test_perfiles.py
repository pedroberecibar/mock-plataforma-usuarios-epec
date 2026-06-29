"""Tests para la regla de capacidad de perfiles por tipo de medidor (ADR-003)."""

from domain.perfiles import soporta_perfiles


def test_clou_soporta_perfiles() -> None:
    assert soporta_perfiles("CLOU") is True


def test_clou_case_insensitive() -> None:
    assert soporta_perfiles("clou") is True


def test_nansen_no_soporta_perfiles() -> None:
    assert soporta_perfiles("NANSEN") is False


def test_desconocido_no_soporta_perfiles() -> None:
    assert soporta_perfiles("CHUPETE") is False


def test_none_no_soporta_perfiles() -> None:
    assert soporta_perfiles(None) is False
