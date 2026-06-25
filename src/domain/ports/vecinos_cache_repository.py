from abc import ABC, abstractmethod


class VecinosCacheRepository(ABC):
    @abstractmethod
    async def upsert(self, suministro_id: str, vecinos: list[str]) -> None: ...
