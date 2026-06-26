"""Fake reversible de PiiCipher para tests (NO es cifrado real)."""

from domain.ports.pii_cipher import PiiCipher

_PREFIX = "enc:"


class FakePiiCipher(PiiCipher):
    def cifrar(self, valor: str) -> str:
        return f"{_PREFIX}{valor}"

    def descifrar(self, token: str) -> str:
        return token.removeprefix(_PREFIX)
