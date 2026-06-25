"""Seeder de demo — datos reales de Oracle + consumo simulado.

Clientes y suministros obtenidos de GEOREF.VM_INTELIGENTES (spike_cliente_seeder.py).
Todos son medidores CLOU del listado-mi-activos.md ubicados en Villa el Libertador, Córdoba.

Uso:
    uv run python scripts/seed_demo.py

NOTA: Si la tabla 'usuarios' ya existe sin la columna 'nombre', borrar la DB primero:
    Remove-Item data/plataforma_clientes.db
"""

import asyncio
import math
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, "src")

from argon2 import PasswordHasher
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.sqlite.models import Base, ConsumoDiario, ConsumoHorario, Suministro, Usuario

DB = "sqlite+aiosqlite:///./data/plataforma_clientes.db"

_ph = PasswordHasher()
_DEFAULT_PASSWORD_HASH = _ph.hash("demo")

# ---------------------------------------------------------------------------
# Datos reales obtenidos de GEOREF.VM_INTELIGENTES (spike_cliente_seeder.py)
# Zona: Villa El Libertador / Santa Isabel / Parque Horizonte — Córdoba
# ---------------------------------------------------------------------------
CLIENTES_ORACLE = [
    {
        "medidor": "70084821",
        "suministro": "590641",
        "nombre": "Moya Teresa Nicolasa",
        "tipo_doc": "DNI",
        "nro_doc": "5918469",
        "cuit": "",
        "domicilio": "Tilcara 674, Villa El Libertador, Córdoba",
        "lat": -31.474377808691,
        "lon": -64.212360550404,
        "tarifa": "140",
        "grupo_tar": "1",
        "telemedible": "CLOU",
        "usuario": "590641",
        "email": "590641@plataforma.epec.com.ar",
    },
    {
        "medidor": "70085039",
        "suministro": "2695309",
        "nombre": "Benitez Natalia Edith",
        "tipo_doc": "DNI",
        "nro_doc": "27132276",
        "cuit": "27271322769",
        "domicilio": "Tilcara 691, Córdoba",
        "lat": -31.474655719664,
        "lon": -64.212772384529,
        "tarifa": "140",
        "grupo_tar": "1",
        "telemedible": "CLOU",
        "usuario": "2695309",
        "email": "2695309@plataforma.epec.com.ar",
    },
    {
        "medidor": "70096451",
        "suministro": "592932",
        "nombre": "Aguero Franco Emiliano",
        "tipo_doc": "DNI",
        "nro_doc": "35526143",
        "cuit": "",
        "domicilio": "Arica 1121, Dpto B, Villa El Libertador, Córdoba",
        "lat": -31.475288765511,
        "lon": -64.219585148189,
        "tarifa": "140",
        "grupo_tar": "1",
        "telemedible": "CLOU",
        "usuario": "592932",
        "email": "592932@plataforma.epec.com.ar",
    },
    {
        "medidor": "70096463",
        "suministro": "592918",
        "nombre": "Villarroel Santiago",
        "tipo_doc": "DNI",
        "nro_doc": "27543025",
        "cuit": "",
        "domicilio": "Arica 1230, Villa El Libertador, Córdoba",
        "lat": -31.47464770215,
        "lon": -64.221020619051,
        "tarifa": "140",
        "grupo_tar": "1",
        "telemedible": "CLOU",
        "usuario": "592918",
        "email": "592918@plataforma.epec.com.ar",
    },
    {
        "medidor": "70096469",
        "suministro": "2925626",
        "nombre": "Velazquez Ismael Francisco",
        "tipo_doc": "DNI",
        "nro_doc": "28657495",
        "cuit": "20286574956",
        "domicilio": "Arica 1213, Dpto 2, Villa El Libertador, Córdoba",
        "lat": -31.474997864232,
        "lon": -64.221024116055,
        "tarifa": "140",
        "grupo_tar": "1",
        "telemedible": "CLOU",
        "usuario": "2925626",
        "email": "2925626@plataforma.epec.com.ar",
    },
    {
        "medidor": "70096527",
        "suministro": "937302",
        "nombre": "Cuello Luz Maria",
        "tipo_doc": "DNI",
        "nro_doc": "11055212",
        "cuit": "",
        "domicilio": "Arica 1185, Villa El Libertador, Córdoba",
        "lat": -31.475130744234,
        "lon": -64.220406429499,
        "tarifa": "140",
        "grupo_tar": "1",
        "telemedible": "CLOU",
        "usuario": "937302",
        "email": "937302@plataforma.epec.com.ar",
    },
    {
        "medidor": "70096530",
        "suministro": "592909",
        "nombre": "Aban Perez Gabriel",
        "tipo_doc": "DNI",
        "nro_doc": "94844867",
        "cuit": "20948448670",
        "domicilio": "Arica 1266, Villa El Libertador, Córdoba",
        "lat": -31.474554911014,
        "lon": -64.221513908329,
        "tarifa": "140",
        "grupo_tar": "1",
        "telemedible": "CLOU",
        "usuario": "592909",
        "email": "592909@plataforma.epec.com.ar",
    },
    {
        "medidor": "70099630",
        "suministro": "1549665",
        "nombre": "Gonzalez Ricardo Alberto Del Corazon De Jesus",
        "tipo_doc": "DNI",
        "nro_doc": "23460268",
        "cuit": "",
        "domicilio": "Manzana 001 Lote 058, Villa El Libertador, Córdoba",
        "lat": -31.46936353413,
        "lon": -64.215648416109,
        "tarifa": "140",
        "grupo_tar": "1",
        "telemedible": "CLOU",
        "usuario": "1549665",
        "email": "1549665@plataforma.epec.com.ar",
    },
    {
        "medidor": "90008245",
        "suministro": "967066",
        "nombre": "Avicola Casusa S.A.S.",
        "tipo_doc": "",
        "nro_doc": "",
        "cuit": "30716897237",
        "domicilio": "Salinas Grandes 1608, Villa El Libertador, Córdoba",
        "lat": -31.467201103232,
        "lon": -64.223717285672,
        "tarifa": "240",
        "grupo_tar": "2",
        "telemedible": "CLOU",
        "usuario": "967066",
        "email": "967066@plataforma.epec.com.ar",
    },
    {
        "medidor": "90008384",
        "suministro": "598845",
        "nombre": "Nicolai Jose Agustin",
        "tipo_doc": "DNI",
        "nro_doc": "20381832",
        "cuit": "20203818328",
        "domicilio": "Arica 1882, Santa Isabel 2A Sección, Córdoba",
        "lat": -31.473322913603,
        "lon": -64.231063633375,
        "tarifa": "240",
        "grupo_tar": "2",
        "telemedible": "CLOU",
        "usuario": "598845",
        "email": "598845@plataforma.epec.com.ar",
    },
    {
        "medidor": "90008578",
        "suministro": "3182201",
        "nombre": "Hak Gisela Judith",
        "tipo_doc": "DNI",
        "nro_doc": "36429951",
        "cuit": "27364299511",
        "domicilio": "Armada Argentina 2061, Santa Isabel 2A Sección, Córdoba",
        "lat": -31.472612109554,
        "lon": -64.230271936904,
        "tarifa": "240",
        "grupo_tar": "2",
        "telemedible": "CLOU",
        "usuario": "3182201",
        "email": "3182201@plataforma.epec.com.ar",
    },
    {
        "medidor": "90008983",
        "suministro": "587652",
        "nombre": "Gonzalez Diana Carolina",
        "tipo_doc": "DNI",
        "nro_doc": "18015003",
        "cuit": "27180150035",
        "domicilio": "Salinas Grandes 1412, Dpto FD, Villa El Libertador, Córdoba",
        "lat": -31.464870650253,
        "lon": -64.220733329085,
        "tarifa": "140",
        "grupo_tar": "1",
        "telemedible": "CLOU",
        "usuario": "587652",
        "email": "587652@plataforma.epec.com.ar",
    },
    {
        "medidor": "90008989",
        "suministro": "3059755",
        "nombre": "Rickand Meat S.A.S.",
        "tipo_doc": "",
        "nro_doc": "",
        "cuit": "30716934183",
        "domicilio": "Av De Mayo 1518, Villa El Libertador, Córdoba",
        "lat": -31.474380584569,
        "lon": -64.225644659409,
        "tarifa": "240",
        "grupo_tar": "2",
        "telemedible": "CLOU",
        "usuario": "3059755",
        "email": "3059755@plataforma.epec.com.ar",
    },
    {
        "medidor": "90010533",
        "suministro": "590834",
        "nombre": "Arlac S.A.",
        "tipo_doc": "",
        "nro_doc": "",
        "cuit": "33708394039",
        "domicilio": "Armada Argentina 826, Parque Atlántica, Córdoba",
        "lat": -31.45811607607,
        "lon": -64.212439103562,
        "tarifa": "240",
        "grupo_tar": "2",
        "telemedible": "CLOU",
        "usuario": "590834",
        "email": "590834@plataforma.epec.com.ar",
    },
    {
        "medidor": "90010534",
        "suministro": "600344",
        "nombre": "Quero Garcia Manuel",
        "tipo_doc": "DNI",
        "nro_doc": "70958",
        "cuit": "20152896590",
        "domicilio": "Av Armada Argentina 665, Parque Horizonte, Córdoba",
        "lat": -31.45774481489,
        "lon": -64.209632842582,
        "tarifa": "240",
        "grupo_tar": "2",
        "telemedible": "CLOU",
        "usuario": "600344",
        "email": "600344@plataforma.epec.com.ar",
    },
]

# Usuario principal para demo completa (18 meses de historia + perfil horario)
USUARIO_DEMO_PRINCIPAL = "592932"  # Aguero Franco Emiliano — suministro 592932

# Suministros en el cluster Arica (Villa El Libertador) — cercanos entre sí (~80-160m)
# Usados como vecinos del usuario principal en las comparaciones
CLUSTER_ARICA = {"592932", "592918", "2925626", "937302", "592909"}


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000.0  # noqa: N806 — convención matemática para radio terrestre
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def kwh_diario(dia: date, grupo_tar: str, seed_offset: float = 0.0) -> float:
    """Consumo diario simulado con variación estacional y ruido."""
    mes = dia.month
    # Invierno (Jun-Ago): pico por calefacción. Verano (Dic-Feb): algo más por AC.
    if grupo_tar == "1":  # Residencial
        base = 15.0 if mes in (6, 7, 8) else 9.0 if mes in (12, 1, 2) else 11.5
    else:  # Comercial/industrial
        base = 38.0 if mes in (6, 7, 8) else 28.0 if mes in (12, 1, 2) else 32.0
    return round(base + seed_offset + random.uniform(-2.0, 2.0), 2)


def perfil_horario_kwh(hora: int, grupo_tar: str, total_dia: float) -> float:
    """Distribución horaria realista. Suma ≈ total_dia (aproximado)."""
    # Perfil residencial: picos a las 7-9h y 19-22h
    if grupo_tar == "1":
        pesos = [
            0.5,
            0.3,
            0.3,
            0.3,
            0.3,
            0.5,  # 0-5h  nocturno bajo
            1.2,
            2.0,
            1.8,
            1.2,
            0.9,
            0.8,  # 6-11h mañana
            0.9,
            0.8,
            0.7,
            0.8,
            1.0,
            1.4,  # 12-17h tarde
            2.0,
            2.5,
            2.0,
            1.8,
            1.2,
            0.7,  # 18-23h noche pico
        ]
    else:
        # Comercial: pico diurno uniforme, baja noche
        pesos = [
            0.3,
            0.2,
            0.2,
            0.2,
            0.3,
            0.5,
            1.5,
            2.5,
            2.8,
            2.8,
            2.8,
            2.7,
            2.7,
            2.8,
            2.8,
            2.7,
            2.5,
            1.8,
            1.0,
            0.5,
            0.4,
            0.3,
            0.3,
            0.3,
        ]
    total_peso = sum(pesos)
    fraccion = pesos[hora] / total_peso
    return round(total_dia * fraccion * random.uniform(0.92, 1.08), 3)


async def seed() -> None:
    engine = create_async_engine(DB, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        print(f"Creando {len(CLIENTES_ORACLE)} suministros y usuarios reales...")

        # ── Suministros ────────────────────────────────────────────────────────
        for c in CLIENTES_ORACLE:
            srv_id = f"SRV-{c['suministro']}"
            stmt = (
                sqlite_insert(Suministro)
                .values(
                    id=srv_id,
                    lat=c["lat"],
                    lon=c["lon"],
                    suministro_referencia=c["suministro"],
                    tarifa_codigo=c["tarifa"],
                )
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        "lat": c["lat"],
                        "lon": c["lon"],
                        "tarifa_codigo": c["tarifa"],
                    },
                )
            )
            await session.execute(stmt)

        # ── Usuarios ────────────────────────────────────────────────────────────
        for c in CLIENTES_ORACLE:
            srv_id = f"SRV-{c['suministro']}"
            stmt = (
                sqlite_insert(Usuario)
                .values(
                    usuario=c["usuario"],
                    suministro_id=srv_id,
                    nombre=c["nombre"],
                    email=c["email"],
                    password_hash=_DEFAULT_PASSWORD_HASH,
                )
                .on_conflict_do_update(
                    index_elements=["usuario"],
                    set_={
                        "suministro_id": srv_id,
                        "nombre": c["nombre"],
                        "email": c["email"],
                        "password_hash": _DEFAULT_PASSWORD_HASH,
                    },
                )
            )
            await session.execute(stmt)

        await session.flush()
        print("  Suministros y usuarios OK.")

        # ── Consumo diario ─────────────────────────────────────────────────────
        random.seed(42)
        hoy = date(2026, 6, 17)
        inicio_historia = date(2025, 1, 1)

        print(f"Generando consumo diario {inicio_historia} a {hoy}...")

        for c in CLIENTES_ORACLE:
            srv_id = f"SRV-{c['suministro']}"
            seed_offset = random.uniform(-1.5, 1.5)
            dia = inicio_historia
            while dia <= hoy:
                kwh = kwh_diario(dia, c["grupo_tar"], seed_offset)
                stmt = (
                    sqlite_insert(ConsumoDiario)
                    .values(suministro_id=srv_id, fecha=dia, kwh=kwh)
                    .on_conflict_do_update(
                        index_elements=["suministro_id", "fecha"],
                        set_={"kwh": kwh},
                    )
                )
                await session.execute(stmt)
                dia += timedelta(days=1)

        await session.flush()
        print("  Consumo diario OK.")

        # ── Consumo horario (últimos 60 días) — todos los suministros ──────────
        print("Generando consumo horario (últimos 60 días)...")
        inicio_horario = hoy - timedelta(days=59)

        for c in CLIENTES_ORACLE:
            srv_id = f"SRV-{c['suministro']}"
            random.seed(int(c["suministro"]))  # seed por suministro para reproducibilidad
            dia = inicio_horario
            while dia <= hoy:
                total_dia = kwh_diario(dia, c["grupo_tar"])
                for hora in range(24):
                    kwh_h = perfil_horario_kwh(hora, c["grupo_tar"], total_dia)
                    stmt = (
                        sqlite_insert(ConsumoHorario)
                        .values(suministro_id=srv_id, fecha=dia, hora=hora, kwh=kwh_h)
                        .on_conflict_do_update(
                            index_elements=["suministro_id", "fecha", "hora"],
                            set_={"kwh": kwh_h},
                        )
                    )
                    await session.execute(stmt)
                dia += timedelta(days=1)

        await session.flush()
        print("  Consumo horario OK.")

        await session.commit()

    await engine.dispose()
    print()
    print("=" * 60)
    print("Demo cargado OK.")
    print()
    print("Usuarios disponibles (password: 'demo' para todos):")
    for c in CLIENTES_ORACLE:
        tag = " [USUARIO PRINCIPAL]" if c["usuario"] == USUARIO_DEMO_PRINCIPAL else ""
        print(f"  usuario={c['usuario']}  ({c['nombre']}) — {c['domicilio']}{tag}")
    print()
    print("Para cambiar passwords:")
    print('  echo "35526143:mi_password" | uv run scripts/seed_passwords.py')


asyncio.run(seed())
