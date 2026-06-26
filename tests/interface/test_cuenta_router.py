from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient

from domain.cuenta import CuentaSuministroRaw
from infrastructure.fakes.auth_provider import FakeAuthProvider
from infrastructure.fakes.cuenta_reader import FakeCuentaReader
from infrastructure.fakes.cuenta_sensible_repository import FakeCuentaSensibleRepository
from infrastructure.fakes.pii_cipher import FakePiiCipher
from infrastructure.fakes.usuario_repository import FakeUsuarioRepository
from interface.cuenta_router import router
from interface.dependencies import (
    get_auth_provider,
    get_cuenta_reader,
    get_cuenta_sensible_repo,
    get_pii_cipher,
    get_usuario_repo,
)


def _raw(**overrides: object) -> CuentaSuministroRaw:
    base: dict[str, object] = {
        "razon_social": "PALACIOS NATALIA",
        "tipo_documento": "DNI",
        "nro_documento": "24241815",
        "cuit": "27242418153",
        "calle": "SAN MARTIN",
        "altura": "100",
        "piso": None,
        "depto": None,
        "torre": None,
        "barrio": "CENTRO",
        "localidad": "CORDOBA",
        "cp": "5000",
        "datos_adicionales": None,
        "estado_servicio": "SN",
        "telemedible": "NANSEN",
        "medidor": "91013486",
        "telemedible_desde": date(2023, 3, 10),
        "codigo_tarifa": "140",
        "tarifa": "1.a/f RESIDENCIAL",
        "grupo_tarifario": "1",
        "clase": "1",
        "clase_descripcion": "1 a-b-f Casas de familia",
        "tension": "1",
        "medidor_fases": "TRI",
    }
    base.update(overrides)
    return CuentaSuministroRaw(**base)  # type: ignore[arg-type]


def build_client(reader: FakeCuentaReader | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(router)

    auth = FakeAuthProvider()
    auth._tokens["tok"] = "demo"
    usuario_repo = FakeUsuarioRepository(
        usuarios={"demo": "SRV-2817670"}, emails={"demo": "demo@epec.com"}
    )

    app.dependency_overrides[get_auth_provider] = lambda: auth
    app.dependency_overrides[get_usuario_repo] = lambda: usuario_repo
    app.dependency_overrides[get_cuenta_reader] = lambda: reader or FakeCuentaReader()
    app.dependency_overrides[get_pii_cipher] = lambda: FakePiiCipher()
    app.dependency_overrides[get_cuenta_sensible_repo] = lambda: FakeCuentaSensibleRepository()
    return TestClient(app)


def test_401_sin_token() -> None:
    client = build_client()
    assert client.get("/cuenta").status_code == 401


def test_404_si_suministro_no_existe_en_oracle() -> None:
    client = build_client(FakeCuentaReader())  # sin datos
    res = client.get("/cuenta", headers={"Authorization": "Bearer tok"})
    assert res.status_code == 404


def test_200_devuelve_secciones() -> None:
    client = build_client(FakeCuentaReader({"SRV-2817670": _raw()}))
    res = client.get("/cuenta", headers={"Authorization": "Bearer tok"})
    assert res.status_code == 200
    body = res.json()
    assert body["personales"]["nombre_o_razon_social"] == "PALACIOS NATALIA"
    assert body["personales"]["nro_documento_masked"] == "****1815"
    assert body["personales"]["email"] == "demo@epec.com"
    assert body["suministro"]["numero"] == "SRV-2817670"
    assert body["suministro"]["direccion"] == "SAN MARTIN 100"
    assert body["tarifa"]["descripcion"] == "1.a/f RESIDENCIAL"
    assert body["medidor"]["marca"] == "NANSEN"
    assert body["medidor"]["fase"] == "Trifásico"
    assert body["medidor"]["inteligente_desde"] == "2023-03-10"


def test_no_filtra_pii_en_claro_en_la_respuesta() -> None:
    client = build_client(FakeCuentaReader({"SRV-2817670": _raw()}))
    res = client.get("/cuenta", headers={"Authorization": "Bearer tok"})
    assert "24241815" not in res.text
    assert "27242418153" not in res.text
