from infrastructure.auth.jwt_auth_provider import JwtAuthProvider


async def test_autenticar_issues_a_token_as_a_login_stub_pending_real_auth() -> None:
    provider = JwtAuthProvider(secret_key="test-secret")

    token = await provider.autenticar("cliente1", "cualquier-password")

    assert token is not None


async def test_verificar_token_returns_the_usuario_encoded_in_a_valid_token() -> None:
    provider = JwtAuthProvider(secret_key="test-secret")
    token = await provider.autenticar("cliente1", "cualquier-password")

    assert await provider.verificar_token(token) == "cliente1"


async def test_verificar_token_returns_none_for_a_malformed_token() -> None:
    provider = JwtAuthProvider(secret_key="test-secret")

    assert await provider.verificar_token("esto-no-es-un-jwt") is None


async def test_verificar_token_returns_none_when_signed_with_a_different_secret() -> None:
    issuer = JwtAuthProvider(secret_key="secret-a")
    verifier = JwtAuthProvider(secret_key="secret-b")
    token = await issuer.autenticar("cliente1", "cualquier-password")

    assert await verifier.verificar_token(token) is None
