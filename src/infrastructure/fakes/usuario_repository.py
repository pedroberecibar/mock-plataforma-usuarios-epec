from domain.ports.usuario_repository import UsuarioRepository


class FakeUsuarioRepository(UsuarioRepository):
    def __init__(
        self,
        usuarios: dict[str, str] | None = None,
        password_hashes: dict[str, str] | None = None,
    ) -> None:
        self._usuarios = usuarios or {}
        self._password_hashes = password_hashes or {}

    async def get_suministro_id(self, usuario: str) -> str | None:
        return self._usuarios.get(usuario)

    async def get_password_hash(self, usuario: str) -> str | None:
        return self._password_hashes.get(usuario)
