from domain.ports.factura_verificacion_port import FacturaVerificacionPort
from infrastructure.fakes.factura_verificacion_port import FakeFacturaVerificacionPort


def test_fake_implementa_el_port() -> None:
    fake = FakeFacturaVerificacionPort()
    assert isinstance(fake, FacturaVerificacionPort)


async def test_fake_devuelve_true_por_defecto() -> None:
    fake = FakeFacturaVerificacionPort()
    result = await fake.verificar_contrato("123", "456")
    assert result is True


async def test_fake_puede_configurarse_para_devolver_false() -> None:
    fake = FakeFacturaVerificacionPort(resultado=False)
    result = await fake.verificar_contrato("123", "456")
    assert result is False


async def test_fake_registra_llamadas() -> None:
    fake = FakeFacturaVerificacionPort()
    await fake.verificar_contrato("NC-1", "CT-99")
    await fake.verificar_contrato("NC-2", "CT-88")
    assert fake.llamadas == [("NC-1", "CT-99"), ("NC-2", "CT-88")]
