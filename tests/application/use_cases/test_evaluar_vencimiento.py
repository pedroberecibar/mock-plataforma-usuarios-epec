"""Tests para EvaluarVencimientoUseCase — RED phase.

Casos:
  1. fecha_vencimiento=None → no emite notificación
  2. (fecha_vencimiento - hoy).days > 5 → no emite
  3. (fecha_vencimiento - hoy).days <= 5 → emite alerta vencimiento_proximo
  4. Alerta ya enviada hoy → no duplica
"""

from datetime import date, timedelta

import pytest

from application.use_cases.evaluar_vencimiento import EvaluarVencimientoUseCase
from infrastructure.fakes.factura_source_reader import FakeFacturaSourceReader
from infrastructure.fakes.notificacion_config_repository import FakeNotificacionConfigRepository
from infrastructure.fakes.notification_sender import FakeNotificationSender

HOY = date(2026, 6, 19)


@pytest.fixture
def notif_repo() -> FakeNotificacionConfigRepository:
    repo = FakeNotificacionConfigRepository()
    return repo


@pytest.fixture
def sender() -> FakeNotificationSender:
    return FakeNotificationSender()


# ---------------------------------------------------------------------------
# Caso 1: fecha_vencimiento=None
# ---------------------------------------------------------------------------


async def test_sin_fecha_vencimiento_no_emite(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    factura_reader = FakeFacturaSourceReader(fecha_vencimiento=None)

    uc = EvaluarVencimientoUseCase(
        factura_reader=factura_reader,
        notificacion_repo=notif_repo,
        notification_sender=sender,
    )
    await uc.ejecutar("S001", email="s001@epec.com.ar", hoy=HOY)

    assert sender.emails_enviados == []


# ---------------------------------------------------------------------------
# Caso 2: vencimiento en > 5 días → no emite
# ---------------------------------------------------------------------------


async def test_vencimiento_lejano_no_emite(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    fecha_vcto = HOY + timedelta(days=6)
    factura_reader = FakeFacturaSourceReader(fecha_vencimiento=fecha_vcto)
    await notif_repo.upsert_config("S001", "vencimiento_proximo", True)

    uc = EvaluarVencimientoUseCase(
        factura_reader=factura_reader,
        notificacion_repo=notif_repo,
        notification_sender=sender,
    )
    await uc.ejecutar("S001", email="s001@epec.com.ar", hoy=HOY)

    assert sender.emails_enviados == []


# ---------------------------------------------------------------------------
# Caso 3: vencimiento en ≤5 días → emite alerta
# ---------------------------------------------------------------------------


async def test_vencimiento_proximo_emite_alerta(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    fecha_vcto = HOY + timedelta(days=5)
    factura_reader = FakeFacturaSourceReader(fecha_vencimiento=fecha_vcto)
    await notif_repo.upsert_config("S001", "vencimiento_proximo", True)

    uc = EvaluarVencimientoUseCase(
        factura_reader=factura_reader,
        notificacion_repo=notif_repo,
        notification_sender=sender,
    )
    await uc.ejecutar("S001", email="s001@epec.com.ar", hoy=HOY)

    assert len(sender.emails_enviados) == 1
    assert sender.emails_enviados[0]["destinatario"] == "s001@epec.com.ar"


# ---------------------------------------------------------------------------
# Caso 4: alerta ya enviada hoy → no duplica
# ---------------------------------------------------------------------------


async def test_vencimiento_proximo_no_duplica(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    fecha_vcto = HOY + timedelta(days=3)
    factura_reader = FakeFacturaSourceReader(fecha_vencimiento=fecha_vcto)
    await notif_repo.upsert_config("S001", "vencimiento_proximo", True)

    from datetime import datetime

    await notif_repo.registrar_enviada("S001", "vencimiento_proximo", datetime(2026, 6, 19, 8, 0))

    uc = EvaluarVencimientoUseCase(
        factura_reader=factura_reader,
        notificacion_repo=notif_repo,
        notification_sender=sender,
    )
    await uc.ejecutar("S001", email="s001@epec.com.ar", hoy=HOY)

    assert sender.emails_enviados == []
