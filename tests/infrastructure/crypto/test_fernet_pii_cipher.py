from infrastructure.crypto.fernet_pii_cipher import FernetPiiCipher


def test_round_trip_recupera_el_valor() -> None:
    cipher = FernetPiiCipher(secret_key="una-clave-de-prueba-cualquiera")
    token = cipher.cifrar("24241815")
    assert cipher.descifrar(token) == "24241815"


def test_ciphertext_no_es_el_plaintext() -> None:
    cipher = FernetPiiCipher(secret_key="otra-clave")
    token = cipher.cifrar("24241815")
    assert "24241815" not in token


def test_misma_clave_descifra_token_de_otra_instancia() -> None:
    token = FernetPiiCipher(secret_key="clave-compartida").cifrar("27242418153")
    assert FernetPiiCipher(secret_key="clave-compartida").descifrar(token) == "27242418153"


def test_claves_distintas_no_descifran() -> None:
    token = FernetPiiCipher(secret_key="clave-A").cifrar("123")
    try:
        FernetPiiCipher(secret_key="clave-B").descifrar(token)
        raise AssertionError("debería fallar con otra clave")
    except Exception:
        pass
