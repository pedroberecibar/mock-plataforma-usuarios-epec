from datetime import date

from domain.cuenta import (
    CuentaSuministroRaw,
    componer_direccion,
    enmascarar,
    normalizar_fase,
)


def _raw(**overrides: object) -> CuentaSuministroRaw:
    base: dict[str, object] = {
        "razon_social": "PALACIOS NATALIA",
        "tipo_documento": "DNI",
        "nro_documento": "24241815",
        "cuit": "27242418153",
        "calle": "MANZANA 014 LOTE 025",
        "altura": None,
        "piso": None,
        "depto": None,
        "torre": None,
        "barrio": "CLAROS DEL BOSQUE",
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


class TestNormalizarFase:
    def test_mon_a_monofasico(self) -> None:
        assert normalizar_fase("MON") == "Monofásico"

    def test_tri_a_trifasico(self) -> None:
        assert normalizar_fase("TRI") == "Trifásico"

    def test_trif_tambien_trifasico(self) -> None:
        assert normalizar_fase("TRIF") == "Trifásico"

    def test_cero_es_desconocido(self) -> None:
        assert normalizar_fase("0") == "Desconocido"

    def test_none_es_desconocido(self) -> None:
        assert normalizar_fase(None) == "Desconocido"


class TestComponerDireccion:
    def test_solo_calle(self) -> None:
        assert componer_direccion(_raw(calle="MANZANA 014 LOTE 025")) == "MANZANA 014 LOTE 025"

    def test_calle_con_altura_y_piso_depto(self) -> None:
        d = componer_direccion(_raw(calle="SAN MARTIN", altura="100", piso="3", depto="B"))
        assert d == "SAN MARTIN 100 Piso 3 Depto B"

    def test_sin_calle_es_none(self) -> None:
        assert componer_direccion(_raw(calle=None)) is None

    def test_anexa_datos_adicionales(self) -> None:
        d = componer_direccion(_raw(calle="X", datos_adicionales="CLAROS DEL BOSQUE II"))
        assert d == "X (CLAROS DEL BOSQUE II)"


class TestEnmascarar:
    def test_documento_deja_ultimos_4(self) -> None:
        assert enmascarar("24241815", 4) == "****1815"

    def test_none_es_none(self) -> None:
        assert enmascarar(None) is None

    def test_valor_corto_se_enmascara_completo(self) -> None:
        assert enmascarar("12", 4) == "**"

    def test_cuit_visibles_3(self) -> None:
        assert enmascarar("27242418153", 3) == "********153"
