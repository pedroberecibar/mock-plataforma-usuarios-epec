from domain.ports.auth_provider import AuthProvider


def get_auth_provider() -> AuthProvider:
    raise NotImplementedError("AuthProvider debe ser wireado en el composition root (src/main.py)")
