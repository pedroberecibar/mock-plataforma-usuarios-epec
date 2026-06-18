function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export async function fetchLinkFactura(
  token: string,
  numeroCliente: string,
  numeroContrato: string
): Promise<string> {
  const params = new URLSearchParams({ numero_cliente: numeroCliente, numero_contrato: numeroContrato });
  const resp = await fetch(`/factura/link?${params}`, { headers: authHeaders(token) });
  if (resp.status === 503) throw new Error("no_configurado");
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const data = (await resp.json()) as { url: string };
  return data.url;
}
