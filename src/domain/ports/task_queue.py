from abc import ABC, abstractmethod
from typing import Any


class TaskQueue(ABC):
    @abstractmethod
    async def encolar(self, nombre_tarea: str, payload: dict[str, Any]) -> str:
        """Encola una tarea asíncrona y devuelve su job id."""
