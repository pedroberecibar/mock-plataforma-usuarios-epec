from domain.ports.cuenta_sensible_repository import CuentaSensibleRepository


class FakeCuentaSensibleRepository(CuentaSensibleRepository):
    def __init__(self) -> None:
        self._store: dict[str, tuple[str | None, str | None]] = {}

    async def upsert(
        self, suministro_id: str, nro_documento_enc: str | None, cuit_enc: str | None
    ) -> None:
        self._store[suministro_id] = (nro_documento_enc, cuit_enc)

    async def get(self, suministro_id: str) -> tuple[str | None, str | None] | None:
        return self._store.get(suministro_id)
