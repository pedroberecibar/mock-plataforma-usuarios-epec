import type { ObjetivoEstadoResponse, ObjetivoSugeridoResponse } from "./types";

const BASE = import.meta.env.VITE_API_URL ?? "";

export interface ObjetivoResponse {
  valor_kwh: number;
  origen: string;
  vigente_desde: string;
}

export async function fetchObjetivo(token: string): Promise<ObjetivoResponse | null> {
  const res = await fetch(`${BASE}/objetivos`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 204 || res.status === 404) return null;
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data: ObjetivoResponse | null = await res.json();
  return data;
}

export async function setObjetivo(token: string, valor_kwh: number): Promise<ObjetivoResponse> {
  const res = await fetch(`${BASE}/objetivos`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ valor_kwh }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<ObjetivoResponse>;
}

export async function fetchObjetivoSugerido(
  token: string,
  mes: string,
): Promise<ObjetivoSugeridoResponse> {
  const res = await fetch(`${BASE}/objetivos/sugerido?mes=${mes}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<ObjetivoSugeridoResponse>;
}

export async function fetchObjetivoEstado(
  token: string,
  mes: string,
): Promise<ObjetivoEstadoResponse> {
  const res = await fetch(`${BASE}/objetivos/estado?mes=${mes}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<ObjetivoEstadoResponse>;
}

export async function evaluarObjetivo(token: string): Promise<void> {
  try {
    await fetch(`${BASE}/alertas/evaluar-objetivo`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch {
    // fire-and-forget: ignorar errores silenciosamente
  }
}
