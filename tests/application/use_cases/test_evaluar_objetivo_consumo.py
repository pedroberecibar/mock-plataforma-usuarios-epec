"""Tests para EvaluarObjetivoConsumoUseCase.

El caso de uso evalúa si el consumo acumulado del mes supera un porcentaje
del objetivo configurado, y en ese caso despacha la alerta OBJETIVO_SUPERADO.

Contrato:
- Si no hay objetivo configurado → no hace nada
- Si consumo < threshold × objetivo → no despacha
- Si consumo >= threshold × objetivo → despacha OBJETIVO_SUPERADO (si habilitada)
- threshold es configurable; default 0.8 (80%)
"""

from datetime import date

import pytest

from application.use_cases.evaluar_alertas import EvaluarAlertasUseCase, TipoAlerta
from application.use_cases.evaluar_objetivo_consumo import EvaluarObjetivoConsumoUseCase
from infrastructure.fakes.consumo_diario_repository import FakeConsumoDiarioRepository
from infrastructure.fakes.notificacion_config_repository import FakeNotificacionConfigRepository
from infrastructure.fakes.notification_sender import FakeNotificationSender
from infrastructure.fakes.objetivo_consumo_repository import FakeObjetivoConsumoRepository

SUMINISTRO = "SRV-001"
MES = date(2026, 6, 1)
HOY = date(2026, 6, 18)


@pytest.fixture
def consumo_repo() -> FakeConsumoDiarioRepository:
    return FakeConsumoDiarioRepository()


@pytest.fixture
def objetivo_repo() -> FakeObjetivoConsumoRepository:
    return FakeObjetivoConsumoRepository()


@pytest.fixture
def notif_repo() -> FakeNotificacionConfigRepository:
    return FakeNotificacionConfigRepository()


@pytest.fixture
def sender() -> FakeNotificationSender:
    return FakeNotificationSender()


@pytest.fixture
def evaluar_alertas(
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> EvaluarAlertasUseCase:
    return EvaluarAlertasUseCase(
        notificacion_repo=notif_repo,
        notification_sender=sender,
        email_destinatario="cliente@example.com",
    )


@pytest.fixture
def uc(
    consumo_repo: FakeConsumoDiarioRepository,
    objetivo_repo: FakeObjetivoConsumoRepository,
    evaluar_alertas: EvaluarAlertasUseCase,
) -> EvaluarObjetivoConsumoUseCase:
    return EvaluarObjetivoConsumoUseCase(
        consumo_repo=consumo_repo,
        objetivo_repo=objetivo_repo,
        evaluar_alertas=evaluar_alertas,
    )


async def test_no_hace_nada_si_no_hay_objetivo(
    uc: EvaluarObjetivoConsumoUseCase,
    sender: FakeNotificationSender,
) -> None:
    await uc.ejecutar(SUMINISTRO, MES, hoy=HOY)
    assert not sender.emails_enviados


async def test_no_despacha_si_consumo_bajo_threshold(
    uc: EvaluarObjetivoConsumoUseCase,
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    sender: FakeNotificationSender,
) -> None:
    await objetivo_repo.upsert_objetivo(SUMINISTRO, 200.0, "manual", MES)
    # 79% del objetivo: no supera el 80% default
    await consumo_repo.upsert_consumo(SUMINISTRO, date(2026, 6, 15), 158.0)

    await uc.ejecutar(SUMINISTRO, MES, hoy=HOY)

    assert not sender.emails_enviados


async def test_despacha_alerta_cuando_consumo_supera_threshold(
    uc: EvaluarObjetivoConsumoUseCase,
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    await objetivo_repo.upsert_objetivo(SUMINISTRO, 200.0, "manual", MES)
    await consumo_repo.upsert_consumo(SUMINISTRO, date(2026, 6, 15), 160.0)  # 80%
    await notif_repo.upsert_config(SUMINISTRO, "objetivo_superado", habilitado=True)

    await uc.ejecutar(SUMINISTRO, MES, hoy=HOY)

    assert len(sender.emails_enviados) == 1
    assert "objetivo" in sender.emails_enviados[0]["asunto"].lower()


async def test_despacha_cuando_consumo_supera_100_pct(
    uc: EvaluarObjetivoConsumoUseCase,
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    await objetivo_repo.upsert_objetivo(SUMINISTRO, 200.0, "manual", MES)
    await consumo_repo.upsert_consumo(SUMINISTRO, date(2026, 6, 15), 210.0)  # 105%
    await notif_repo.upsert_config(SUMINISTRO, "objetivo_superado", habilitado=True)

    await uc.ejecutar(SUMINISTRO, MES, hoy=HOY)

    assert len(sender.emails_enviados) == 1


async def test_threshold_configurable(
    consumo_repo: FakeConsumoDiarioRepository,
    objetivo_repo: FakeObjetivoConsumoRepository,
    evaluar_alertas: EvaluarAlertasUseCase,
    notif_repo: FakeNotificacionConfigRepository,
    sender: FakeNotificationSender,
) -> None:
    uc_60 = EvaluarObjetivoConsumoUseCase(
        consumo_repo=consumo_repo,
        objetivo_repo=objetivo_repo,
        evaluar_alertas=evaluar_alertas,
        threshold=0.6,
    )
    await objetivo_repo.upsert_objetivo(SUMINISTRO, 200.0, "manual", MES)
    await consumo_repo.upsert_consumo(SUMINISTRO, date(2026, 6, 15), 120.0)  # 60%
    await notif_repo.upsert_config(SUMINISTRO, "objetivo_superado", habilitado=True)

    await uc_60.ejecutar(SUMINISTRO, MES, hoy=HOY)

    assert len(sender.emails_enviados) == 1


async def test_no_despacha_si_alerta_deshabilitada(
    uc: EvaluarObjetivoConsumoUseCase,
    objetivo_repo: FakeObjetivoConsumoRepository,
    consumo_repo: FakeConsumoDiarioRepository,
    sender: FakeNotificationSender,
) -> None:
    await objetivo_repo.upsert_objetivo(SUMINISTRO, 200.0, "manual", MES)
    await consumo_repo.upsert_consumo(SUMINISTRO, date(2026, 6, 15), 180.0)  # 90%
    # notif_repo no tiene objetivo_superado habilitado

    await uc.ejecutar(SUMINISTRO, MES, hoy=HOY)

    assert not sender.emails_enviados


async def test_objetivo_superado_es_tipo_alerta_valido() -> None:
    assert TipoAlerta.OBJETIVO_SUPERADO == "objetivo_superado"
