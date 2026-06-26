import type { CuentaResponse } from "./types";

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

/**
 * GET /cuenta — datos que EPEC tiene del cliente (solo lectura).
 *
 * Errores señalizados como mensajes específicos para que la UI los distinga:
 *   - 503 → "no_configurado" (Oracle no disponible, igual que api/factura.ts)
 *   - 404 → "sin_datos" (no se encontraron datos del suministro)
 *   - otros → "HTTP <status>"
 */
export async function fetchCuenta(token: string): Promise<CuentaResponse> {
  const resp = await fetch("/cuenta", { headers: authHeaders(token) });
  if (resp.status === 503) throw new Error("no_configurado");
  if (resp.status === 404) throw new Error("sin_datos");
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json() as Promise<CuentaResponse>;
}
