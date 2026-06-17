import type { ComparacionResponse, DiarioResponse } from "./types";

const BASE = "";

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function fetchSerieDiaria(
  token: string,
  suministroId: string,
  desde: string,
  hasta: string
): Promise<DiarioResponse> {
  const url = `${BASE}/consumo/${suministroId}/diario?desde=${desde}&hasta=${hasta}`;
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<DiarioResponse>;
}

export async function fetchComparacion(
  token: string,
  suministroId: string,
  mes: string
): Promise<ComparacionResponse> {
  const url = `${BASE}/consumo/${suministroId}/comparacion?mes=${mes}`;
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<ComparacionResponse>;
}
