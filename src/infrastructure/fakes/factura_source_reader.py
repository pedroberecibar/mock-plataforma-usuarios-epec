from datetime import date, timedelta

from domain.ports.factura_source_reader import (
    FacturaCuenta,
    FacturaDocumento,
    FacturaResult,
    FacturaSourceReader,
)


class FakeFacturaSourceReader(FacturaSourceReader):
    def __init__(
        self,
        fecha_vencimiento: date | None = None,
        dias_vencimiento: int | None = None,
        importe: float = 12345.67,
    ) -> None:
        if fecha_vencimiento is not None:
            self._fecha_vcto: date | None = fecha_vencimiento
        elif dias_vencimiento is not None:
            self._fecha_vcto = date.today() + timedelta(days=dias_vencimiento)
        else:
            self._fecha_vcto = date.today() + timedelta(days=5)
        self._importe = importe

    async def get_factura(self, suministro_id: str) -> FacturaResult | None:
        return FacturaResult(fecha_vencimiento=self._fecha_vcto, importe=self._importe)

    async def get_cuenta_factura(self, suministro_id: str) -> FacturaCuenta | None:
        return FacturaCuenta(
            documentos=[
                FacturaDocumento(
                    periodo="07/2026",
                    importe=self._importe,
                    fecha_vencimiento=self._fecha_vcto,
                    estado="pagar",
                    url_pdf=None,
                )
            ],
            total_deuda=self._importe,
            pago_online=True,
            cliente_id="1109294",
            contrato_id="0281767003",
        )
