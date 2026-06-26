from domain.ports.factura_identificadores import (
    FacturaIdentificadores,
    FacturaIdentificadoresCache,
    FacturaIdentificadoresReader,
)


class FakeFacturaIdentificadoresReader(FacturaIdentificadoresReader):
    def __init__(self, mapa: dict[str, FacturaIdentificadores] | None = None) -> None:
        self._mapa = mapa or {}
        self.llamadas: list[str] = []

    async def leer(self, suministro_id: str) -> FacturaIdentificadores | None:
        self.llamadas.append(suministro_id)
        return self._mapa.get(suministro_id)


class FakeFacturaIdentificadoresCache(FacturaIdentificadoresCache):
    def __init__(self, mapa: dict[str, FacturaIdentificadores] | None = None) -> None:
        self._store: dict[str, FacturaIdentificadores] = dict(mapa or {})

    async def get(self, suministro_id: str) -> FacturaIdentificadores | None:
        return self._store.get(suministro_id)

    async def guardar(self, suministro_id: str, ids: FacturaIdentificadores) -> None:
        self._store[suministro_id] = ids
