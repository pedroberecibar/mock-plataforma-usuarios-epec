"""Script para setear password_hash en usuarios de producción.

Uso:
    uv run scripts/seed_passwords.py [--db DATABASE_URL]

Lee líneas "usuario:password" desde stdin (una por línea).
Líneas vacías y comentarios (#) son ignorados.
Las contraseñas NUNCA pasan por argumentos CLI para evitar que queden en logs.

Ejemplos:
    echo "demo:secreto123" | uv run scripts/seed_passwords.py
    uv run scripts/seed_passwords.py < usuarios.txt
    uv run scripts/seed_passwords.py  # modo interactivo
"""

import asyncio
import getpass
import os
import sys

sys.path.insert(0, "src")

from argon2 import PasswordHasher
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.sqlite.models import Usuario

_ph = PasswordHasher()


def parse_args() -> str:
    db_url = "sqlite+aiosqlite:///./data/plataforma_clientes.db"
    args = sys.argv[1:]
    if "--db" in args:
        idx = args.index("--db")
        try:
            db_url = args[idx + 1]
        except IndexError:
            print("Error: --db requiere un valor", file=sys.stderr)
            sys.exit(1)
    return os.environ.get("DATABASE_URL", db_url)


def read_pairs() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []

    if sys.stdin.isatty():
        print("Modo interactivo — ingresá usuarios (vacío para terminar):")
        while True:
            usuario = input("  usuario: ").strip()
            if not usuario:
                break
            password = getpass.getpass(f"  password para '{usuario}': ")
            if not password:
                print(f"  -> Saltando '{usuario}' (password vacío)")
                continue
            pairs.append((usuario, password))
    else:
        for linea in sys.stdin:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if ":" not in linea:
                print(
                    f"Advertencia: línea ignorada (formato esperado 'usuario:password'): {linea!r}",
                    file=sys.stderr,
                )
                continue
            usuario, password = linea.split(":", 1)
            usuario = usuario.strip()
            password = password.strip()
            if not usuario or not password:
                print(
                    f"Advertencia: usuario o password vacío, ignorando: {linea!r}", file=sys.stderr
                )
                continue
            pairs.append((usuario, password))

    return pairs


async def seed_passwords(db_url: str, pairs: list[tuple[str, str]]) -> None:
    engine = create_async_engine(db_url, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        for usuario, password in pairs:
            result = await session.execute(select(Usuario).where(Usuario.usuario == usuario))
            row = result.scalar_one_or_none()
            if row is None:
                print(f"[SKIP]    '{usuario}' — no encontrado en la DB")
                continue

            password_hash = _ph.hash(password)
            await session.execute(
                update(Usuario)
                .where(Usuario.usuario == usuario)
                .values(password_hash=password_hash)
            )
            print(f"[OK]      '{usuario}' — hash actualizado")

        await session.commit()

    await engine.dispose()
    print(f"\n{len(pairs)} usuario(s) procesado(s).")


def main() -> None:
    db_url = parse_args()
    pairs = read_pairs()

    if not pairs:
        print("No se proporcionaron usuarios. Saliendo.")
        sys.exit(0)

    print(f"\nActualizando {len(pairs)} usuario(s) en {db_url} ...")
    asyncio.run(seed_passwords(db_url, pairs))


if __name__ == "__main__":
    main()
