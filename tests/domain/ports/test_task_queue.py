import pytest

from domain.ports.task_queue import TaskQueue


def test_is_abstract_and_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        TaskQueue()  # type: ignore[abstract]


def test_declares_encolar_as_abstract() -> None:
    assert TaskQueue.__abstractmethods__ == frozenset({"encolar"})
