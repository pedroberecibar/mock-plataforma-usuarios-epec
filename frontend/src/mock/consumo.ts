import type {
  AnomaliaResponse,
  ComparacionResponse,
  DetalleDiaResponse,
  DiarioResponse,
  HoraPicoResponse,
  SerieHorariaResponse,
} from "../api/types";
import { fixture } from "./_fixtures";

export async function fetchSerieDiaria(
  _token: string,
  _suministroId: string,
  desde: string,
  hasta: string
): Promise<DiarioResponse> {
  const all = await fixture<DiarioResponse>("diario");
  const filtered = all.serie.filter((p) => p.fecha >= desde && p.fecha <= hasta);
  return { serie: filtered, datos_hasta: all.datos_hasta };
}

export async function fetchDetalleDia(
  _token: string,
  fecha: string
): Promise<DetalleDiaResponse> {
  const map = await fixture<Record<string, DetalleDiaResponse>>("detalle-dia");
  return (
    map[fecha] ?? {
      fecha,
      kwh_dia: null,
      kwh_mismo_dia_anio_ant: null,
      kwh_promedio_zona: null,
      n_vecinos: 0,
    }
  );
}

export async function fetchComparacion(
  _token: string,
  _suministroId: string,
  _mes: string
): Promise<ComparacionResponse> {
  return fixture<ComparacionResponse>("comparacion");
}

/** Vista anual de vecinos: replica la comparación del fixture para cada mes pedido. */
export async function fetchComparacionAnual(
  token: string,
  suministroId: string,
  meses: string[]
): Promise<ComparacionResponse[]> {
  return Promise.all(meses.map((mes) => fetchComparacion(token, suministroId, mes)));
}

export async function fetchAnomalia(
  _token: string,
  _mes: string
): Promise<AnomaliaResponse | null> {
  return fixture<AnomaliaResponse | null>("anomalia");
}

export async function fetchHoraPico(
  _token: string,
  _mes: string
): Promise<HoraPicoResponse | null> {
  const perfil = Array.from({ length: 24 }, (_, h) => ({
    hora: h,
    kwh: h >= 18 && h <= 22 ? 0.75 + Math.random() * 0.3 : 0.2 + Math.random() * 0.2,
  }));
  return { hora_pico: 20, kwh_promedio: 0.85, perfil_24h: perfil };
}

export async function fetchSerieHoraria(
  _token: string,
  fecha: string
): Promise<SerieHorariaResponse> {
  const serie = Array.from({ length: 24 }, (_, h) => ({
    hora: h,
    kwh: h >= 18 && h <= 22 ? 0.7 + Math.random() * 0.4 : 0.15 + Math.random() * 0.25,
  }));
  return { fecha, serie };
}
