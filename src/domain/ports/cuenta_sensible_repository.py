import abc


class CuentaSensibleRepository(abc.ABC):
    """Persiste datos personales sensibles (PII) ya cifrados, por suministro.

    El repositorio guarda y devuelve tokens opacos; el cifrado/descifrado es
    responsabilidad de `PiiCipher`. Nunca recibe ni almacena texto claro.
    """

    @abc.abstractmethod
    async def upsert(
        self, suministro_id: str, nro_documento_enc: str | None, cuit_enc: str | None
    ) -> None:
        """Crea o actualiza los valores cifrados del suministro."""

    @abc.abstractmethod
    async def get(self, suministro_id: str) -> tuple[str | None, str | None] | None:
        """Devuelve (nro_documento_enc, cuit_enc) o None si no hay registro."""
