from typing import Any
from uuid import uuid4

from domain.ports.task_queue import TaskQueue


class FakeTaskQueue(TaskQueue):
    def __init__(self) -> None:
        self.tareas_encoladas: list[tuple[str, dict[str, Any]]] = []

    async def encolar(self, nombre_tarea: str, payload: dict[str, Any]) -> str:
        self.tareas_encoladas.append((nombre_tarea, payload))
        return str(uuid4())
