"""Tests para EvaluarAlertasUseCase.

El caso de uso evalúa qué alertas deben enviarse para un suministro dado:
- Solo envía si el tipo está habilitado en notificaciones_config
- Solo envía si no se envió ya hoy (deduplicación vía notificaciones_enviadas)
- Registra el envío después de hacerlo
"""

from datetime import date, datetime

import pytest

from application.use_cases.evaluar_alertas import EvaluarAlertasUseCase, TipoAlerta
from infrastructure.fakes.notificacion_config_repository import FakeNotificacionConfigRepository
from infrastructure.fakes.notification_sender import FakeNotificationSender


@pytest.fixture
def notif_repo() -> FakeNotificacionConfigRepository:
    return FakeNotificacionConfigRepository()


@pytest.fixture
def sender() -> FakeNotificationSender:
    return FakeNotificationSender()


@pytest.fixture
def uc(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> EvaluarAlertasUseCase:
    return EvaluarAlertasUseCase(
        notificacion_repo=notif_repo,
        notification_sender=sender,
        email_destinatario="cliente@example.com",
    )


async def test_no_envía_si_tipo_deshabilitado(
    uc: EvaluarAlertasUseCase,
    sender: FakeNotificationSender,
) -> None:
    hoy = date(2026, 6, 18)
    await uc.ejecutar(
        suministro_id="SRV-001",
        tipos=[TipoAlerta.FACTURA_DISPONIBLE],
        hoy=hoy,
    )
    assert not sender.emails_enviados


async def test_envia_si_tipo_habilitado(
    uc: EvaluarAlertasUseCase,
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    await notif_repo.upsert_config("SRV-001", "factura_disponible", habilitado=True)
    hoy = date(2026, 6, 18)

    await uc.ejecutar(
        suministro_id="SRV-001",
        tipos=[TipoAlerta.FACTURA_DISPONIBLE],
        hoy=hoy,
    )

    assert len(sender.emails_enviados) == 1
    assert "factura" in sender.emails_enviados[0]["asunto"].lower()


async def test_no_envia_si_ya_enviada_hoy(
    uc: EvaluarAlertasUseCase,
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    await notif_repo.upsert_config("SRV-001", "factura_disponible", habilitado=True)
    await notif_repo.registrar_enviada("SRV-001", "factura_disponible", datetime(2026, 6, 18, 8, 0))
    hoy = date(2026, 6, 18)

    await uc.ejecutar(
        suministro_id="SRV-001",
        tipos=[TipoAlerta.FACTURA_DISPONIBLE],
        hoy=hoy,
    )

    assert not sender.emails_enviados


async def test_registra_envio_en_notificaciones_enviadas(
    uc: EvaluarAlertasUseCase,
    notif_repo: FakeNotificacionConfigRepository,
) -> None:
    await notif_repo.upsert_config("SRV-001", "factura_disponible", habilitado=True)
    hoy = date(2026, 6, 18)

    await uc.ejecutar(
        suministro_id="SRV-001",
        tipos=[TipoAlerta.FACTURA_DISPONIBLE],
        hoy=hoy,
    )

    assert await notif_repo.ya_enviada_hoy("SRV-001", "factura_disponible", hoy)


async def test_envía_múltiples_tipos_habilitados(
    uc: EvaluarAlertasUseCase,
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    await notif_repo.upsert_config("SRV-001", "factura_disponible", habilitado=True)
    await notif_repo.upsert_config("SRV-001", "vencimiento_proximo", habilitado=True)
    hoy = date(2026, 6, 18)

    await uc.ejecutar(
        suministro_id="SRV-001",
        tipos=[TipoAlerta.FACTURA_DISPONIBLE, TipoAlerta.VENCIMIENTO_PROXIMO],
        hoy=hoy,
    )

    assert len(sender.emails_enviados) == 2
