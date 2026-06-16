import pytest

from domain.ports.notification_sender import NotificationSender


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        NotificationSender()  # type: ignore[abstract]


def test_declares_enviar_push_and_enviar_email_as_abstract() -> None:
    assert NotificationSender.__abstractmethods__ == frozenset({"enviar_push", "enviar_email"})
