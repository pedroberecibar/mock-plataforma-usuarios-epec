from datetime import date, timedelta

from domain.ports.factura_source_reader import FacturaResult, FacturaSourceReader


class FakeFacturaSourceReader(FacturaSourceReader):
    def __init__(
        self,
        fecha_vencimiento: date | None = None,
        dias_vencimiento: int | None = None,
    ) -> None:
        if fecha_vencimiento is not None:
            self._fecha_vcto: date | None = fecha_vencimiento
        elif dias_vencimiento is not None:
            self._fecha_vcto = date.today() + timedelta(days=dias_vencimiento)
        else:
            self._fecha_vcto = date.today() + timedelta(days=5)

    async def get_factura(self, suministro_id: str) -> FacturaResult | None:
        return FacturaResult(fecha_vencimiento=self._fecha_vcto)
