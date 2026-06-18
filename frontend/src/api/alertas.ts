export interface AlertaConfigItem {
  tipo: string;
  habilitado: boolean;
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
}

export async function fetchAlertasConfig(token: string): Promise<AlertaConfigItem[]> {
  const resp = await fetch("/alertas/config", { headers: authHeaders(token) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<AlertaConfigItem[]>;
}

export async function patchAlertaConfig(
  token: string,
  tipo: string,
  habilitado: boolean,
): Promise<AlertaConfigItem> {
  const resp = await fetch("/alertas/config", {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify({ tipo, habilitado }),
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<AlertaConfigItem>;
}
