from typing import Protocol


class PoblarUseCase(Protocol):
    async def ejecutar(self, suministro_id: str, forzar: bool = False) -> None: ...
