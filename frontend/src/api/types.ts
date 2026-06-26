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
  serie: PuntoSerie[];
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
  zona_mes_actual: ComparacionZonaResponse | null;
  datos_hasta: string | null;
}

export interface FacturaDocumento {
  periodo: string | null; // "MM/YYYY"
  importe: number | null;
  fecha_vencimiento: string | null; // "YYYY-MM-DD"
  estado: string | null;
  url_pdf: string | null;
}

export interface FacturaDatosResponse {
  total_deuda: number;
  pago_online: boolean;
  cliente_id: string | null;
  contrato_id: string | null;
  documentos: FacturaDocumento[];
}

export interface DocumentoPago {
  periodo: string;
  nro_factura: string;
  importe: number;
  fecha_vencimiento: string;
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

export interface PuntoSerieHoraria {
  hora: number; // 0-23
  kwh: number;
}

export interface SerieHorariaResponse {
  fecha: string; // "YYYY-MM-DD"
  serie: PuntoSerieHoraria[];
}

export interface HoraPicoResponse {
  hora_pico: number; // 0-23
  kwh_promedio: number;
  perfil_24h: PuntoSerieHoraria[];
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
  consumo_acumulado_kwh: number | null;
  consumo_promedio_diario_kwh: number | null;
}
