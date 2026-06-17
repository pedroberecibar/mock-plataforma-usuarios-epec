import type { HomeResponse } from "./types";

const BASE = "";

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function fetchHome(
  token: string,
  suministroId: string,
  mes: string
): Promise<HomeResponse> {
  const url = `${BASE}/home/${suministroId}?mes=${mes}`;
  const resp = await fetch(url, { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<HomeResponse>;
}
