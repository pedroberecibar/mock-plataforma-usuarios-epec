from domain.cuenta import CuentaSuministroRaw
from domain.ports.cuenta_reader import CuentaReader


class FakeCuentaReader(CuentaReader):
    def __init__(self, datos: dict[str, CuentaSuministroRaw] | None = None) -> None:
        self._datos = datos or {}

    def set(self, suministro_id: str, raw: CuentaSuministroRaw) -> None:
        self._datos[suministro_id] = raw

    async def leer_cuenta(self, suministro_id: str) -> CuentaSuministroRaw | None:
        return self._datos.get(suministro_id)
