import pytest

from application.use_cases.obtener_documentos_factura import ObtenerDocumentosFacturaUseCase
from domain.documento_pago import DocumentoPago
from domain.ports.factura_verificacion_port import FacturaVerificacionPort

_DOC = DocumentoPago(
    periodo="04/2026",
    nro_factura="0001-00000123",
    importe=15230.50,
    fecha_vencimiento="2026-05-15",
)


class _FakePort(FacturaVerificacionPort):
    def __init__(
        self,
        documentos: list[DocumentoPago] | None = None,
        contrato_invalido: bool = False,
    ) -> None:
        self._documentos = documentos if documentos is not None else []
        self._contrato_invalido = contrato_invalido

    async def verificar_contrato(self, numero_cliente: str, numero_contrato: str) -> bool:
        return not self._contrato_invalido

    async def obtener_documentos(
        self, numero_cliente: str, numero_contrato: str
    ) -> list[DocumentoPago]:
        if self._contrato_invalido:
            raise ValueError(f"Contrato {numero_contrato} no encontrado")
        return self._documentos


async def test_retorna_documentos_del_port() -> None:
    uc = ObtenerDocumentosFacturaUseCase(verificacion_port=_FakePort(documentos=[_DOC]))

    result = await uc.ejecutar("1109294", "0281767003")

    assert result == [_DOC]


async def test_retorna_lista_vacia_si_no_hay_documentos() -> None:
    uc = ObtenerDocumentosFacturaUseCase(verificacion_port=_FakePort(documentos=[]))

    result = await uc.ejecutar("1109294", "0281767003")

    assert result == []


async def test_propaga_error_si_contrato_invalido() -> None:
    uc = ObtenerDocumentosFacturaUseCase(verificacion_port=_FakePort(contrato_invalido=True))

    with pytest.raises(ValueError, match="Contrato"):
        await uc.ejecutar("1109294", "invalido")
