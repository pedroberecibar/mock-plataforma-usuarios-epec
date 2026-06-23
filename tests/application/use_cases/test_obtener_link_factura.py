import pytest

from application.use_cases.obtener_link_factura import ObtenerLinkFacturaUseCase
from domain.documento_pago import DocumentoPago
from domain.ports.factura_verificacion_port import FacturaVerificacionPort


class _FakeVerificacion(FacturaVerificacionPort):
    def __init__(self, resultado: bool = True) -> None:
        self._resultado = resultado
        self.llamadas: list[tuple[str, str]] = []

    async def verificar_contrato(self, numero_cliente: str, numero_contrato: str) -> bool:
        self.llamadas.append((numero_cliente, numero_contrato))
        return self._resultado

    async def obtener_documentos(
        self, numero_cliente: str, numero_contrato: str
    ) -> list[DocumentoPago]:
        return []


async def test_ejecutar_llama_port_con_los_datos_correctos() -> None:
    port = _FakeVerificacion(resultado=True)
    uc = ObtenerLinkFacturaUseCase(verificacion_port=port, base_url="https://epec.com.ar/factura")

    await uc.ejecutar(numero_cliente="123456", numero_contrato="789012")

    assert port.llamadas == [("123456", "789012")]


async def test_ejecutar_devuelve_base_url_si_verificacion_ok() -> None:
    port = _FakeVerificacion(resultado=True)
    uc = ObtenerLinkFacturaUseCase(verificacion_port=port, base_url="https://epec.com.ar/factura")

    url = await uc.ejecutar("123456", "789012")

    assert url == "https://epec.com.ar/factura"


async def test_ejecutar_devuelve_url_por_defecto_si_base_url_es_none() -> None:
    port = _FakeVerificacion(resultado=True)
    uc = ObtenerLinkFacturaUseCase(verificacion_port=port, base_url=None)

    url = await uc.ejecutar("1", "2")

    assert url == "https://www.epec.com.ar/tramites/pagos"


async def test_ejecutar_lanza_error_si_verificacion_falla() -> None:
    port = _FakeVerificacion(resultado=False)
    uc = ObtenerLinkFacturaUseCase(verificacion_port=port, base_url=None)

    with pytest.raises(ValueError, match="Contrato"):
        await uc.ejecutar("1", "2")
