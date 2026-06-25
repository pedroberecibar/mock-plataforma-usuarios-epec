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
