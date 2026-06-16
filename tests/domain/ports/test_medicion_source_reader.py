import pytest

from domain.ports.medicion_source_reader import MedicionSourceReader


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        MedicionSourceReader()  # type: ignore[abstract]


def test_declares_leer_lecturas_as_abstract() -> None:
    assert MedicionSourceReader.__abstractmethods__ == frozenset({"leer_lecturas"})
