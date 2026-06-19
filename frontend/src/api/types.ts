export interface PuntoSerie {
  fecha: string; // "YYYY-MM-DD"
  kwh: number;
}

export interface ProyeccionResponse {
  mes: string;
  metodo_aplicado: string;
  bandera_confianza: string;
  rango_inferior_kwh: number | null;
  rango_superior_kwh: number | null;
}

export interface ConsumoMesResponse {
  total_kwh: number | null;
  vs_mes_anterior_pct: number | null;
  vs_anio_anterior_pct: number | null;
}

export interface ComparacionZonaResponse {
  promedio_vecinos_kwh: number | null;
  n_vecinos: number;
  diferencia_pct: number | null;
}

export interface HomeResponse {
  consumo_mes: ConsumoMesResponse;
  comparacion_zona: ComparacionZonaResponse;
  proyeccion: ProyeccionResponse;
  datos_hasta: string | null;
  timestamp: string;
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

export interface FacturaDatosResponse {
  fecha_vencimiento: string | null; // "YYYY-MM-DD"
}

export interface DetalleDiaResponse {
  fecha: string; // "YYYY-MM-DD"
  kwh_dia: number | null;
  kwh_mismo_dia_anio_ant: number | null;
  kwh_promedio_zona: number | null;
  n_vecinos: number;
}

export interface ObjetivoSugeridoResponse {
  valor_kwh: number | null;
  n_vecinos: number;
  sin_datos: boolean;
}

export type TextoDinamico =
  | "bajo_ritmo"
  | "en_ritmo"
  | "sobre_ritmo"
  | "agotado"
  | "sin_objetivo";

export interface AnomaliaResponse {
  fecha: string; // "YYYY-MM-DD"
  kwh: number;
  z_score: number;
  desviacion_pct: number;
}

export interface ObjetivoEstadoResponse {
  objetivo_kwh: number | null;
  promedio_vecinos_kwh: number | null;
  n_vecinos: number;
  diferencia_pct: number | null;
  dias_transcurridos: number;
  dias_objetivo_consumidos: number | null;
  texto_dinamico: TextoDinamico;
  excedente_kwh: number | null;
  consumo_diario_real_kwh: number | null;
  consumo_diario_objetivo_kwh: number | null;
}
