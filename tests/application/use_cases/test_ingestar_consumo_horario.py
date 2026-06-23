"""Tests TDD para IngestarConsumoHorarioUseCase. Todos usan Fakes — sin I/O real."""

from datetime import date

import pytest

from application.use_cases.ingestar_consumo_horario import IngestarConsumoHorarioUseCase
from domain.lecturas_horarias import LecturaHoraria
from infrastructure.fakes.consumo_horario_repository import FakeConsumoHorarioRepository
from infrastructure.fakes.medicion_horaria_source_reader import (
    SEED_LECTURAS_HORARIAS,
    FakeMedicionHorariaSourceReader,
)
from infrastructure.fakes.suministro_repository import FakeSuministroRepository


def _lectura(
    equipo: str,
    fecha: date,
    hora: int,
    valor: float,
    cdr: str = "E",
    srv: str | None = None,
) -> LecturaHoraria:
    return LecturaHoraria(
        equipo=equipo,
        srv_codigo=srv if srv is not None else f"SRV-{equipo}",
        cdr_codigo=cdr,
        fecha=fecha,
        hora=hora,
        valor_kwh=valor,
    )


D = date(2026, 6, 1)


async def test_dos_lecturas_consecutivas_generan_kwh_correcto() -> None:
    """L[hora0]=1000, L[hora1]=1000.5 → consumo hora 0 = 0.5 kWh."""
    reader = FakeMedicionHorariaSourceReader(
        lecturas=[_lectura("E1", D, 0, 1000.0), _lectura("E1", D, 1, 1000.5)]
    )
    repo = FakeConsumoHorarioRepository()
    await IngestarConsumoHorarioUseCase(reader, repo, FakeSuministroRepository()).ejecutar(D, D)

    serie = await repo.get_serie_horaria("SRV-E1", D)
    assert len(serie) == 1
    hora, kwh = serie[0]
    assert hora == 0
    assert kwh == pytest.approx(0.5, abs=0.01)


async def test_ultima_lectura_no_genera_consumo() -> None:
    """La lectura final no tiene siguiente → no genera registro."""
    reader = FakeMedicionHorariaSourceReader(
        lecturas=[
            _lectura("E1", D, 0, 1000.0),
            _lectura("E1", D, 1, 1000.6),
            _lectura("E1", D, 2, 1001.3),
        ]
    )
    repo = FakeConsumoHorarioRepository()
    await IngestarConsumoHorarioUseCase(reader, repo, FakeSuministroRepository()).ejecutar(D, D)

    serie = await repo.get_serie_horaria("SRV-E1", D)
    horas = {h for h, _ in serie}
    assert 2 not in horas  # hora 2 es la última — sin siguiente
    assert len(serie) == 2


async def test_gap_horario_distribuye_tasa_uniforme() -> None:
    """Gap de 3 horas (hora 0 → hora 3): (1001.2-1000.0)/3 por hora."""
    reader = FakeMedicionHorariaSourceReader(
        lecturas=[_lectura("E1", D, 0, 1000.0), _lectura("E1", D, 3, 1001.2)]
    )
    repo = FakeConsumoHorarioRepository()
    await IngestarConsumoHorarioUseCase(reader, repo, FakeSuministroRepository()).ejecutar(D, D)

    serie = await repo.get_serie_horaria("SRV-E1", D)
    assert len(serie) == 3
    for _hora, kwh in serie:
        assert kwh == pytest.approx(0.4, abs=0.01)


async def test_cruce_de_dia_genera_consumo_en_hora_23() -> None:
    """Lectura en hora 23 del día d y hora 0 del día d+1 → consumo para hora 23."""
    d1 = date(2026, 6, 2)
    reader = FakeMedicionHorariaSourceReader(
        lecturas=[
            _lectura("E1", D, 23, 1100.0),
            _lectura("E1", d1, 0, 1100.7),
        ]
    )
    repo = FakeConsumoHorarioRepository()
    await IngestarConsumoHorarioUseCase(reader, repo, FakeSuministroRepository()).ejecutar(D, d1)

    serie_d = await repo.get_serie_horaria("SRV-E1", D)
    assert any(hora == 23 and kwh == pytest.approx(0.7, abs=0.01) for hora, kwh in serie_d)


async def test_delta_negativo_se_omite() -> None:
    """Reset de contador (valor siguiente < actual) → par descartado."""
    reader = FakeMedicionHorariaSourceReader(
        lecturas=[
            _lectura("E1", D, 0, 1000.0),
            _lectura("E1", D, 1, 500.0),  # reset
            _lectura("E1", D, 2, 501.0),
        ]
    )
    repo = FakeConsumoHorarioRepository()
    await IngestarConsumoHorarioUseCase(reader, repo, FakeSuministroRepository()).ejecutar(D, D)

    serie = await repo.get_serie_horaria("SRV-E1", D)
    horas = {h for h, _ in serie}
    assert 0 not in horas  # par (hora0→hora1) descartado por delta negativo
    assert 1 in horas  # par (hora1→hora2) es válido


async def test_cdr_no_e_se_ignora() -> None:
    """Registros con cdr_codigo != 'E' no generan consumo."""
    reader = FakeMedicionHorariaSourceReader(
        lecturas=[
            _lectura("E1", D, 0, 1000.0),
            _lectura("E1", D, 1, 999_999.0, cdr="R"),  # debe ignorarse
            _lectura("E1", D, 2, 1000.8),
        ]
    )
    repo = FakeConsumoHorarioRepository()
    await IngestarConsumoHorarioUseCase(reader, repo, FakeSuministroRepository()).ejecutar(D, D)

    serie = await repo.get_serie_horaria("SRV-E1", D)
    kwhs = [kwh for _, kwh in serie]
    assert all(kwh < 10 for kwh in kwhs), "No deben aparecer valores de registro R"


async def test_dedupe_por_equipo_fecha_hora() -> None:
    """Duplicados (mismo equipo+fecha+hora) se deduplicación antes del cálculo."""
    reader = FakeMedicionHorariaSourceReader(
        lecturas=[
            _lectura("E1", D, 0, 1000.0),
            _lectura("E1", D, 0, 1000.0),  # duplicado exacto
            _lectura("E1", D, 1, 1000.5),
        ]
    )
    repo = FakeConsumoHorarioRepository()
    await IngestarConsumoHorarioUseCase(reader, repo, FakeSuministroRepository()).ejecutar(D, D)

    serie = await repo.get_serie_horaria("SRV-E1", D)
    assert len(serie) == 1
    _, kwh = serie[0]
    assert kwh == pytest.approx(0.5, abs=0.01)


async def test_dos_equipos_se_procesan_independientemente() -> None:
    """Cada equipo genera su propia serie sin interferencia."""
    reader = FakeMedicionHorariaSourceReader(
        lecturas=[
            _lectura("E1", D, 0, 1000.0),
            _lectura("E1", D, 1, 1001.0),
            _lectura("E2", D, 0, 500.0, srv="SRV-E2"),
            _lectura("E2", D, 1, 500.3, srv="SRV-E2"),
        ]
    )
    repo = FakeConsumoHorarioRepository()
    await IngestarConsumoHorarioUseCase(reader, repo, FakeSuministroRepository()).ejecutar(D, D)

    serie_e1 = await repo.get_serie_horaria("SRV-E1", D)
    serie_e2 = await repo.get_serie_horaria("SRV-E2", D)
    assert len(serie_e1) == 1 and serie_e1[0][1] == pytest.approx(1.0, abs=0.01)
    assert len(serie_e2) == 1 and serie_e2[0][1] == pytest.approx(0.3, abs=0.01)


async def test_suministro_placeholder_se_crea() -> None:
    """El suministro placeholder se crea antes de persistir consumo horario."""
    reader = FakeMedicionHorariaSourceReader(
        lecturas=[_lectura("E1", D, 0, 1000.0), _lectura("E1", D, 1, 1000.5)]
    )
    repo = FakeConsumoHorarioRepository()
    suministro_repo = FakeSuministroRepository()
    await IngestarConsumoHorarioUseCase(reader, repo, suministro_repo).ejecutar(D, D)

    assert await suministro_repo.existe("SRV-E1")


async def test_integracion_semilla_completa() -> None:
    """End-to-end con seed: la ingesta produce valores plausibles sin nulos."""
    reader = FakeMedicionHorariaSourceReader(SEED_LECTURAS_HORARIAS)
    repo = FakeConsumoHorarioRepository()
    resultado = await IngestarConsumoHorarioUseCase(
        reader, repo, FakeSuministroRepository()
    ).ejecutar(date(2026, 6, 1), date(2026, 6, 30))

    assert resultado.suministros_procesados >= 1
    assert resultado.horas_procesadas > 0

    serie = await repo.get_serie_horaria("SRV-91013496", date(2026, 6, 10))
    assert len(serie) > 0
    for hora, kwh in serie:
        assert 0 <= hora <= 23
        assert kwh > 0
