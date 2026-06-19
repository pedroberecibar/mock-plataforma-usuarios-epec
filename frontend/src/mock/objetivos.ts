import type { ObjetivoEstadoResponse, ObjetivoSugeridoResponse } from "../api/types";
import { fixture } from "./_fixtures";

export interface ObjetivoResponse {
  valor_kwh: number;
  origen: string;
  vigente_desde: string;
}

export async function fetchObjetivo(_token: string): Promise<ObjetivoResponse | null> {
  return null;
}

export async function setObjetivo(
  _token: string,
  _valor_kwh: number
): Promise<ObjetivoResponse> {
  throw new Error("No disponible en modo demo");
}

export async function fetchObjetivoSugerido(
  _token: string,
  _mes: string
): Promise<ObjetivoSugeridoResponse> {
  return fixture<ObjetivoSugeridoResponse>("objetivos-sugerido");
}

export async function fetchObjetivoEstado(
  _token: string,
  _mes: string
): Promise<ObjetivoEstadoResponse> {
  return fixture<ObjetivoEstadoResponse>("objetivos-estado");
}

export async function evaluarObjetivo(_token: string): Promise<void> {
  // no-op en modo demo
}
