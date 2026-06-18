from infrastructure.fakes.auth_provider import FakeAuthProvider


async def test_autenticar_returns_a_token() -> None:
    """autenticar es un stub de generación de token; no verifica credenciales."""
    provider = FakeAuthProvider()

    token = await provider.autenticar("cualquier_usuario", "cualquier_password")

    assert token is not None


async def test_verificar_token_returns_the_user_id_for_a_valid_token() -> None:
    provider = FakeAuthProvider()
    token = await provider.autenticar("cliente1", "clave123")

    assert await provider.verificar_token(token) == "cliente1"


async def test_verificar_token_returns_none_for_an_unknown_token() -> None:
    provider = FakeAuthProvider()

    assert await provider.verificar_token("token-inexistente") is None


async def test_verificar_password_compara_plaintext() -> None:
    """FakeAuthProvider.verificar_password compara plaintext (sin hashing real)."""
    provider = FakeAuthProvider()

    assert provider.verificar_password("clave123", "clave123") is True
    assert provider.verificar_password("incorrecta", "clave123") is False
