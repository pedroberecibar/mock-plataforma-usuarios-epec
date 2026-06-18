from domain.ports.usuario_repository import UsuarioRepository


class FakeUsuarioRepository(UsuarioRepository):
    def __init__(self, usuarios: dict[str, str] | None = None) -> None:
        self._usuarios = usuarios or {}

    async def get_suministro_id(self, usuario: str) -> str | None:
        return self._usuarios.get(usuario)
