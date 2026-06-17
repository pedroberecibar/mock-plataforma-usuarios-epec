export interface PuntoSerie {
  fecha: string; // "YYYY-MM-DD"
  kwh: number;
}

export interface DiarioResponse {
  serie: PuntoSerie[];
  datos_hasta: string | null;
}

export interface PeriodoConsumo {
  mes: string; // "YYYY-MM-DD" (primer día del mes)
  serie: PuntoSerie[];
  total_kwh: number | null;
}

export interface ComparacionResponse {
  mes_actual: PeriodoConsumo;
  mes_anterior: PeriodoConsumo;
  mismo_mes_anio_anterior: PeriodoConsumo;
  datos_hasta: string | null;
}
