export interface PerfilResponse {
  nombre: string | null;
  nro_suministro: string;
  suministro_id: string;
  tarifa_codigo: string | null;
}

export async function fetchPerfil(token: string): Promise<PerfilResponse> {
  const resp = await fetch("/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resp.ok) throw new Error("Error al obtener perfil");
  return resp.json() as Promise<PerfilResponse>;
}
