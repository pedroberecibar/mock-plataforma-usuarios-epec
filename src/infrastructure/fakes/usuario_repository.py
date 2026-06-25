from domain.ports.usuario_repository import UsuarioRepository


class FakeUsuarioRepository(UsuarioRepository):
    def __init__(
        self,
        usuarios: dict[str, str] | None = None,
        password_hashes: dict[str, str] | None = None,
        emails: dict[str, str] | None = None,
        nombres: dict[str, str] | None = None,
    ) -> None:
        self._usuarios = usuarios or {}
        self._password_hashes = password_hashes or {}
        self._emails = emails or {}
        self._nombres = nombres or {}

    async def get_suministro_id(self, usuario: str) -> str | None:
        return self._usuarios.get(usuario)

    async def get_password_hash(self, usuario: str) -> str | None:
        return self._password_hashes.get(usuario)

    async def get_email(self, usuario: str) -> str | None:
        return self._emails.get(usuario)

    async def get_nombre(self, usuario: str) -> str | None:
        return self._nombres.get(usuario)
