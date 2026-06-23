import type { AnomaliaResponse, ComparacionResponse, DetalleDiaResponse, DiarioResponse, HoraPicoResponse, SerieHorariaResponse } from "./types";

const BASE = "";

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function fetchSerieDiaria(
  token: string,
  _suministroId: string,
  desde: string,
  hasta: string
): Promise<DiarioResponse> {
  const url = `${BASE}/consumo/diario?desde=${desde}&hasta=${hasta}`;
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<DiarioResponse>;
}

export async function fetchDetalleDia(
  token: string,
  fecha: string
): Promise<DetalleDiaResponse> {
  const url = `${BASE}/consumo/dia?fecha=${fecha}`;
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<DetalleDiaResponse>;
}

export async function fetchComparacion(
  token: string,
  _suministroId: string,
  mes: string
): Promise<ComparacionResponse> {
  const url = `${BASE}/consumo/comparacion?mes=${mes}`;
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<ComparacionResponse>;
}

export async function fetchAnomalia(
  token: string,
  mes: string
): Promise<AnomaliaResponse | null> {
  const url = `${BASE}/consumo/anomalia?mes=${mes}`;
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<AnomaliaResponse | null>;
}

export async function fetchSerieHoraria(
  token: string,
  fecha: string
): Promise<SerieHorariaResponse> {
  const url = `${BASE}/consumo/horario?fecha=${fecha}`;
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<SerieHorariaResponse>;
}

export async function fetchHoraPico(
  token: string,
  mes: string
): Promise<HoraPicoResponse | null> {
  const url = `${BASE}/consumo/hora-pico?mes=${mes}`;
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<HoraPicoResponse | null>;
}
