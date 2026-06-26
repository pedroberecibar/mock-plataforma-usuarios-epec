import abc


class PiiCipher(abc.ABC):
    """Puerto de cifrado simétrico para datos personales sensibles (PII).

    Cifra/descifra strings (ej. nro de documento, CUIT) para persistirlos en
    reposo sin texto claro. El adapter concreto define el algoritmo.
    """

    @abc.abstractmethod
    def cifrar(self, valor: str) -> str:
        """Devuelve el token cifrado (texto) del valor en claro."""

    @abc.abstractmethod
    def descifrar(self, token: str) -> str:
        """Devuelve el valor en claro a partir del token cifrado."""
