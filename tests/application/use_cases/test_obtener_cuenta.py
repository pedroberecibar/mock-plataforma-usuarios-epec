from datetime import date

from application.use_cases.obtener_cuenta import ObtenerCuentaUseCase
from domain.cuenta import CuentaSuministroRaw
from infrastructure.fakes.cuenta_reader import FakeCuentaReader
from infrastructure.fakes.cuenta_sensible_repository import FakeCuentaSensibleRepository
from infrastructure.fakes.pii_cipher import FakePiiCipher
from infrastructure.fakes.usuario_repository import FakeUsuarioRepository


def _raw(**overrides: object) -> CuentaSuministroRaw:
    base: dict[str, object] = {
        "razon_social": "PALACIOS NATALIA",
        "tipo_documento": "DNI",
        "nro_documento": "24241815",
        "cuit": "27242418153",
        "calle": "SAN MARTIN",
        "altura": "100",
        "piso": "3",
        "depto": "B",
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


def _build(reader: FakeCuentaReader) -> tuple[ObtenerCuentaUseCase, FakeCuentaSensibleRepository]:
    usuario_repo = FakeUsuarioRepository(
        usuarios={"demo": "SRV-2817670"}, emails={"demo": "demo@epec.com"}
    )
    sensible = FakeCuentaSensibleRepository()
    uc = ObtenerCuentaUseCase(
        cuenta_reader=reader,
        usuario_repo=usuario_repo,
        pii_cipher=FakePiiCipher(),
        sensible_repo=sensible,
    )
    return uc, sensible


async def test_devuelve_none_si_no_hay_datos_oracle() -> None:
    uc, _ = _build(FakeCuentaReader())
    assert await uc.ejecutar("demo", "SRV-2817670") is None


async def test_compone_todas_las_secciones() -> None:
    reader = FakeCuentaReader({"SRV-2817670": _raw()})
    uc, _ = _build(reader)

    res = await uc.ejecutar("demo", "SRV-2817670")

    assert res is not None
    assert res.personales.nombre_o_razon_social == "PALACIOS NATALIA"
    assert res.personales.email == "demo@epec.com"
    assert res.personales.nro_documento_masked == "****1815"
    assert res.personales.cuit_masked == "********153"
    assert res.suministro.numero == "SRV-2817670"
    assert res.suministro.direccion == "SAN MARTIN 100 Piso 3 Depto B"
    assert res.tarifa.descripcion == "1.a/f RESIDENCIAL"
    assert res.tarifa.clase_descripcion == "1 a-b-f Casas de familia"
    assert res.medidor.numero == "91013486"
    assert res.medidor.marca == "NANSEN"
    assert res.medidor.fase == "Trifásico"
    assert res.medidor.inteligente_desde == date(2023, 3, 10)


async def test_nunca_expone_pii_en_claro() -> None:
    reader = FakeCuentaReader({"SRV-2817670": _raw()})
    uc, _ = _build(reader)
    res = await uc.ejecutar("demo", "SRV-2817670")
    assert res is not None
    assert "24241815" not in (res.personales.nro_documento_masked or "")
    assert "27242418153" not in (res.personales.cuit_masked or "")


async def test_persiste_pii_cifrada() -> None:
    reader = FakeCuentaReader({"SRV-2817670": _raw()})
    uc, sensible = _build(reader)
    await uc.ejecutar("demo", "SRV-2817670")
    # FakePiiCipher prefija con "enc:"; el repo guarda el token, no el claro
    assert await sensible.get("SRV-2817670") == ("enc:24241815", "enc:27242418153")


async def test_gc_empresa_sin_dni_usa_cuit() -> None:
    reader = FakeCuentaReader(
        {"SRV-2817670": _raw(nro_documento=None, cuit="30708021642", telemedible="GC")}
    )
    uc, sensible = _build(reader)
    res = await uc.ejecutar("demo", "SRV-2817670")
    assert res is not None
    assert res.personales.nro_documento_masked is None
    assert res.personales.cuit_masked == "********642"
    assert await sensible.get("SRV-2817670") == (None, "enc:30708021642")


async def test_degrada_campos_faltantes_a_none() -> None:
    reader = FakeCuentaReader({"SRV-2817670": _raw(calle=None, medidor=None, medidor_fases=None)})
    uc, _ = _build(reader)
    res = await uc.ejecutar("demo", "SRV-2817670")
    assert res is not None
    assert res.suministro.direccion is None
    assert res.medidor.numero is None
    assert res.medidor.fase == "Desconocido"


async def test_nansen_no_soporta_perfiles() -> None:
    reader = FakeCuentaReader({"SRV-2817670": _raw(telemedible="NANSEN")})
    uc, _ = _build(reader)
    res = await uc.ejecutar("demo", "SRV-2817670")
    assert res is not None
    assert res.medidor.soporta_perfiles is False


async def test_clou_soporta_perfiles() -> None:
    reader = FakeCuentaReader({"SRV-2817670": _raw(telemedible="CLOU")})
    uc, _ = _build(reader)
    res = await uc.ejecutar("demo", "SRV-2817670")
    assert res is not None
    assert res.medidor.soporta_perfiles is True
