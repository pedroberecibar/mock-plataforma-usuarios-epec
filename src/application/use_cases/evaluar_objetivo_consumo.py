from datetime import UTC, date, datetime

from application.use_cases.evaluar_alertas import EvaluarAlertasUseCase, TipoAlerta
from domain.ports.consumo_diario_repository import ConsumoDiarioRepository
from domain.ports.objetivo_consumo_repository import ObjetivoConsumoRepository

_DEFAULT_THRESHOLD = 0.8


class EvaluarObjetivoConsumoUseCase:
    def __init__(
        self,
        consumo_repo: ConsumoDiarioRepository,
        objetivo_repo: ObjetivoConsumoRepository,
        evaluar_alertas: EvaluarAlertasUseCase,
        threshold: float = _DEFAULT_THRESHOLD,
    ) -> None:
        self._consumo_repo = consumo_repo
        self._objetivo_repo = objetivo_repo
        self._evaluar_alertas = evaluar_alertas
        self._threshold = threshold

    async def ejecutar(
        self,
        suministro_id: str,
        mes: date,
        hoy: date | None = None,
    ) -> None:
        objetivo = await self._objetivo_repo.get_vigente(suministro_id)
        if objetivo is None:
            return

        valor_kwh, _, _ = objetivo
        hoy_real = hoy or datetime.now(UTC).date()
        desde = mes.replace(day=1)

        serie = await self._consumo_repo.get_serie(suministro_id, desde, hoy_real)
        total = sum(kwh for _, kwh in serie)

        if total >= self._threshold * valor_kwh:
            await self._evaluar_alertas.ejecutar(
                suministro_id=suministro_id,
                tipos=[TipoAlerta.OBJETIVO_SUPERADO],
                hoy=hoy_real,
            )
