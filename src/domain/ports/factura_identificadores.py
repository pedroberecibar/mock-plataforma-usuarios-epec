import abc
from dataclasses import dataclass

CONTRATO_LEN = 10
CONTRATO_SUFIJO_LEN = 2


@dataclass(frozen=True)
class FacturaIdentificadores:
    """IDs comerciales que la API de facturación de EPEC exige por suministro."""

    cliente_id: str
    contrato_id: str


def construir_contrato_id(suministro: str | int, contrato: str | int) -> str:
    """Arma el `contratoId` de 10 dígitos que espera la API de EPEC.

    Concatena el número de suministro con el contrato (expresado en 2 dígitos) y,
    si el resultado tiene menos de 10 dígitos, lo rellena con ceros a la izquierda.
    Ej.: suministro 2817670 + contrato 3 -> "0281767003".
    """
    contrato_2 = str(contrato).zfill(CONTRATO_SUFIJO_LEN)
    return (str(suministro) + contrato_2).zfill(CONTRATO_LEN)


class FacturaIdentificadoresReader(abc.ABC):
    """Resuelve cliente/contrato de un suministro desde la fuente de verdad (Oracle)."""

    @abc.abstractmethod
    async def leer(self, suministro_id: str) -> FacturaIdentificadores | None:
        """Devuelve los identificadores del suministro, o None si no existen."""


class FacturaIdentificadoresCache(abc.ABC):
    """Cachea cliente/contrato por suministro para no pegarle a Oracle en cada request."""

    @abc.abstractmethod
    async def get(self, suministro_id: str) -> FacturaIdentificadores | None:
        """Devuelve los identificadores cacheados, o None si no hay registro."""

    @abc.abstractmethod
    async def guardar(self, suministro_id: str, ids: FacturaIdentificadores) -> None:
        """Crea o actualiza los identificadores cacheados del suministro."""
