from infrastructure.sqlite.models import Base

EXPECTED_TABLES = {
    "suministros": {"id", "lat", "lon", "suministro_referencia", "tarifa_codigo", "telemedible"},
    "consumo_diario": {"suministro_id", "fecha", "kwh"},
    "consumo_horario": {"suministro_id", "fecha", "hora", "kwh"},
    "objetivo_consumo": {"id", "suministro_id", "valor_kwh", "origen", "vigente_desde"},
    "proyeccion_mensual": {
        "suministro_id",
        "mes",
        "metodo_aplicado",
        "meses_usados_como_base",
        "dias_usados_como_base",
        "bandera_confianza",
        "rango_inferior_kwh",
        "rango_superior_kwh",
    },
    "notificaciones_config": {"usuario_id", "tipo", "canal", "habilitado"},
    "factura_redireccion": {"id", "suministro_id", "numero_cliente", "numero_contrato"},
    "usuarios": {"usuario", "suministro_id", "nombre", "email", "password_hash"},
    "notificaciones_enviadas": {"id", "suministro_id", "tipo_alerta", "fecha_envio"},
    "vecinos_cache": {"suministro_id", "vecinos_json", "updated_at"},
    "cuenta_datos_sensibles": {
        "suministro_id",
        "nro_documento_enc",
        "cuit_enc",
        "actualizado_en",
    },
}


def test_declares_all_tables_from_modelo_de_datos_clave() -> None:
    assert set(Base.metadata.tables.keys()) == set(EXPECTED_TABLES.keys())


def test_each_table_declares_its_expected_columns() -> None:
    for table_name, expected_columns in EXPECTED_TABLES.items():
        actual_columns = set(Base.metadata.tables[table_name].columns.keys())
        assert actual_columns == expected_columns, table_name
