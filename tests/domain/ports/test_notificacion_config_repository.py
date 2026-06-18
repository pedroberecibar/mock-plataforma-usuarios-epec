import pytest

from domain.ports.notificacion_config_repository import NotificacionConfigRepository


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        NotificacionConfigRepository()  # type: ignore[abstract]


def test_declares_expected_abstract_methods() -> None:
    assert NotificacionConfigRepository.__abstractmethods__ == frozenset(
        {"get_config", "upsert_config", "ya_enviada_hoy", "registrar_enviada"}
    )
