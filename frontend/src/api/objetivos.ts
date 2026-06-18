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
