from infrastructure.fakes.auth_provider import FakeAuthProvider


async def test_autenticar_returns_a_token_for_valid_credentials() -> None:
    provider = FakeAuthProvider(usuarios={"cliente1": "clave123"})

    token = await provider.autenticar("cliente1", "clave123")

    assert token is not None


async def test_autenticar_returns_none_for_invalid_credentials() -> None:
    provider = FakeAuthProvider(usuarios={"cliente1": "clave123"})

    assert await provider.autenticar("cliente1", "incorrecta") is None


async def test_verificar_token_returns_the_user_id_for_a_valid_token() -> None:
    provider = FakeAuthProvider(usuarios={"cliente1": "clave123"})
    token = await provider.autenticar("cliente1", "clave123")

    assert await provider.verificar_token(token) == "cliente1"


async def test_verificar_token_returns_none_for_an_unknown_token() -> None:
    provider = FakeAuthProvider(usuarios={"cliente1": "clave123"})

    assert await provider.verificar_token("token-inexistente") is None
