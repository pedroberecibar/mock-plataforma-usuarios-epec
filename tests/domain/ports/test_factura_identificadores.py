from domain.ports.factura_identificadores import construir_contrato_id


def test_contrato_id_caso_real_2817670() -> None:
    # suministro 2817670 + contrato 3 -> 281767003 (9 díg) -> pad a 10
    assert construir_contrato_id("2817670", "3") == "0281767003"


def test_contrato_id_rellena_contrato_a_dos_digitos() -> None:
    # el contrato siempre se expresa con 2 dígitos antes de concatenar
    assert construir_contrato_id("937302", "2") == "0093730202"


def test_contrato_id_acepta_enteros() -> None:
    assert construir_contrato_id(2817670, 3) == "0281767003"


def test_contrato_id_contrato_ya_de_dos_digitos() -> None:
    # contrato de 2 díg. no se vuelve a rellenar
    assert construir_contrato_id("590641", "12") == "0059064112"


def test_contrato_id_siempre_diez_digitos() -> None:
    assert len(construir_contrato_id("100005", "1")) == 10
