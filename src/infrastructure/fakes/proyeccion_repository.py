from datetime import date

from domain.ports.proyeccion_repository import ProyeccionRepository
from domain.proyeccion import ProyeccionMensual


class FakeProyeccionRepository(ProyeccionRepository):
    def __init__(self) -> None:
        self._store: dict[tuple[str, date], ProyeccionMensual] = {}

    async def get_proyeccion(self, suministro_id: str, mes: date) -> ProyeccionMensual | None:
        return self._store.get((suministro_id, mes))

    async def upsert_proyeccion(self, proyeccion: ProyeccionMensual) -> None:
        self._store[(proyeccion.suministro_id, proyeccion.mes)] = proyeccion
