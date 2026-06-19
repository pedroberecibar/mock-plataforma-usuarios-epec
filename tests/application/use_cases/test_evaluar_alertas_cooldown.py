"""Tests para el rate-limit de notificaciones (CU-A06).

Verifica que EvaluarAlertasUseCase suprima reenvíos dentro del cooldown
configurado por tipo de alerta.
"""

from datetime import datetime, timedelta

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


async def test_suprime_envio_dentro_del_cooldown(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    await notif_repo.upsert_config("SRV-001", "consumo_anomalo", habilitado=True)
    ahora = datetime(2026, 6, 18, 12, 0, 0)
    hace_3h = ahora - timedelta(hours=3)
    await notif_repo.registrar_enviada("SRV-001", "consumo_anomalo", hace_3h)

    uc = EvaluarAlertasUseCase(
        notificacion_repo=notif_repo,
        notification_sender=sender,
        email_destinatario="test@example.com",
    )
    await uc.ejecutar(
        suministro_id="SRV-001",
        tipos=[TipoAlerta.CONSUMO_ANOMALO],
        hoy=ahora.date(),
        ahora=ahora,
    )

    assert not sender.emails_enviados


async def test_permite_envio_fuera_del_cooldown(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    await notif_repo.upsert_config("SRV-001", "consumo_anomalo", habilitado=True)
    ahora = datetime(2026, 6, 18, 12, 0, 0)
    hace_8h = ahora - timedelta(hours=8)
    await notif_repo.registrar_enviada("SRV-001", "consumo_anomalo", hace_8h)

    uc = EvaluarAlertasUseCase(
        notificacion_repo=notif_repo,
        notification_sender=sender,
        email_destinatario="test@example.com",
    )
    await uc.ejecutar(
        suministro_id="SRV-001",
        tipos=[TipoAlerta.CONSUMO_ANOMALO],
        hoy=ahora.date(),
        ahora=ahora,
    )

    assert len(sender.emails_enviados) == 1


async def test_cooldown_objetivo_superado_12h(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    await notif_repo.upsert_config("SRV-001", "objetivo_superado", habilitado=True)
    ahora = datetime(2026, 6, 18, 14, 0, 0)
    hace_10h = ahora - timedelta(hours=10)
    await notif_repo.registrar_enviada("SRV-001", "objetivo_superado", hace_10h)

    uc = EvaluarAlertasUseCase(
        notificacion_repo=notif_repo,
        notification_sender=sender,
        email_destinatario="test@example.com",
    )
    await uc.ejecutar(
        suministro_id="SRV-001",
        tipos=[TipoAlerta.OBJETIVO_SUPERADO],
        hoy=ahora.date(),
        ahora=ahora,
    )

    assert not sender.emails_enviados


async def test_primer_envio_sin_historial_no_suprimido(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    await notif_repo.upsert_config("SRV-001", "consumo_anomalo", habilitado=True)
    ahora = datetime(2026, 6, 18, 12, 0, 0)

    uc = EvaluarAlertasUseCase(
        notificacion_repo=notif_repo,
        notification_sender=sender,
        email_destinatario="test@example.com",
    )
    await uc.ejecutar(
        suministro_id="SRV-001",
        tipos=[TipoAlerta.CONSUMO_ANOMALO],
        hoy=ahora.date(),
        ahora=ahora,
    )

    assert len(sender.emails_enviados) == 1
