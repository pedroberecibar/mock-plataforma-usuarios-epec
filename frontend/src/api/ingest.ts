function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function triggerPoblar(token: string): Promise<void> {
  try {
    await fetch("/ingest/poblar", {
      method: "POST",
      headers: authHeaders(token),
    });
  } catch {
    // fire-and-forget: errores de red no bloquean el flujo del usuario
  }
}

export interface RefrescoResult {
  ok: boolean;
  datos_hasta: string | null;
}

// Refresco síncrono (botón "Actualizar"): espera a que termine la ingesta desde Oracle.
// A diferencia de triggerPoblar, propaga el error para que la UI lo refleje.
export async function refrescarConsumo(token: string): Promise<RefrescoResult> {
  const r = await fetch("/ingest/refrescar", {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!r.ok) {
    throw new Error(`Error ${r.status} al actualizar`);
  }
  return (await r.json()) as RefrescoResult;
}
