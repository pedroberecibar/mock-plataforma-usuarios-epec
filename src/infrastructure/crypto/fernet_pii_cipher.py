"""Adapter de PiiCipher con Fernet (cryptography).

La clave Fernet (32 bytes urlsafe-base64) se deriva determinísticamente del
`SECRET_KEY` de la app vía SHA-256, así no hace falta gestionar una clave
separada. Fernet provee cifrado autenticado (AES-128-CBC + HMAC).
"""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet

from domain.ports.pii_cipher import PiiCipher


class FernetPiiCipher(PiiCipher):
    def __init__(self, secret_key: str) -> None:
        digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(digest))

    def cifrar(self, valor: str) -> str:
        return self._fernet.encrypt(valor.encode("utf-8")).decode("ascii")

    def descifrar(self, token: str) -> str:
        return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")
