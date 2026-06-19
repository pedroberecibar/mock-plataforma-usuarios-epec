import type {
  AnomaliaResponse,
  ComparacionResponse,
  DetalleDiaResponse,
  DiarioResponse,
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

export async function fetchAnomalia(
  _token: string,
  _mes: string
): Promise<AnomaliaResponse | null> {
  return fixture<AnomaliaResponse | null>("anomalia");
}
