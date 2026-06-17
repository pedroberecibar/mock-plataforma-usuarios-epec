from datetime import date

from domain.lecturas import LecturaTelemedida
from domain.ports.medicion_source_reader import MedicionSourceReader

# ---------------------------------------------------------------------------
# Dataset semilla representativo de medidores EPEC
# Cubre: 2 equipos, lecturas acumulativas ~200-400 kWh/mes, gap de 5 días en
# equipo "91013496" (enero), un registro con cdr_codigo != 'E', y un duplicado
# intencional que el ETL debe deduplicar.
#
# Mapeo fake medidor → suministro (en Oracle real: XXSIGEC.EQUIPOS):
#   equipo "91013496" → srv_codigo "SRV-91013496"
#   equipo "91013497" → srv_codigo "SRV-91013497"
# ---------------------------------------------------------------------------
SEED_LECTURAS_EPEC: list[LecturaTelemedida] = [
    # --- Equipo 91013496 (enero → junio 2026) ---
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 1, 1), 12_400.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 1, 8), 12_465.00),
    # gap intencional: sin lectura del 9 al 13 de enero
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 1, 14), 12_540.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 1, 21), 12_610.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 1, 28), 12_678.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 2, 4), 12_745.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 2, 11), 12_812.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 2, 18), 12_878.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 2, 25), 12_943.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 3, 4), 13_010.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 3, 11), 13_076.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 3, 18), 13_140.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 3, 25), 13_202.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 4, 1), 13_265.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 4, 8), 13_328.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 4, 15), 13_388.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 4, 22), 13_446.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 4, 29), 13_503.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 5, 6), 13_559.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 5, 13), 13_614.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 5, 20), 13_668.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 5, 27), 13_721.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 6, 3), 13_773.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 6, 10), 13_824.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 6, 17), 13_874.00),
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 6, 24), 13_923.00),
    # registro con cdr_codigo != 'E' — debe filtrarse en el ETL
    LecturaTelemedida("91013496", "SRV-91013496", "R", date(2026, 6, 10), 999_999.00),
    # duplicado intencional — mismo (equipo, fecha, cdr='E'), debe deduplicarse
    LecturaTelemedida("91013496", "SRV-91013496", "E", date(2026, 6, 3), 13_773.00),
    # --- Equipo 91013497 (mayo → junio 2026) ---
    LecturaTelemedida("91013497", "SRV-91013497", "E", date(2026, 5, 1), 8_200.00),
    LecturaTelemedida("91013497", "SRV-91013497", "E", date(2026, 5, 8), 8_260.00),
    LecturaTelemedida("91013497", "SRV-91013497", "E", date(2026, 5, 15), 8_318.00),
    LecturaTelemedida("91013497", "SRV-91013497", "E", date(2026, 5, 22), 8_375.00),
    LecturaTelemedida("91013497", "SRV-91013497", "E", date(2026, 5, 29), 8_431.00),
    LecturaTelemedida("91013497", "SRV-91013497", "E", date(2026, 6, 5), 8_487.00),
    LecturaTelemedida("91013497", "SRV-91013497", "E", date(2026, 6, 12), 8_542.00),
    LecturaTelemedida("91013497", "SRV-91013497", "E", date(2026, 6, 19), 8_596.00),
    LecturaTelemedida("91013497", "SRV-91013497", "E", date(2026, 6, 26), 8_649.00),
]


class FakeMedicionSourceReader(MedicionSourceReader):
    def __init__(self, lecturas: list[LecturaTelemedida] | None = None) -> None:
        self._lecturas = lecturas if lecturas is not None else list(SEED_LECTURAS_EPEC)

    async def leer_lecturas(self, desde: date, hasta: date) -> list[LecturaTelemedida]:
        """Devuelve lecturas en [desde, hasta] más la última lectura por equipo
        anterior a `desde` (ancla), replicando el comportamiento de OracleMedicionReader."""
        en_rango = [lect for lect in self._lecturas if desde <= lect.fecha <= hasta]

        anclas: dict[str, LecturaTelemedida] = {}
        for lect in self._lecturas:
            if lect.fecha < desde and (
                lect.equipo not in anclas or lect.fecha > anclas[lect.equipo].fecha
            ):
                anclas[lect.equipo] = lect

        return en_rango + list(anclas.values())
