export interface PerfilResponse {
  nombre: string | null;
  nro_suministro: string;
  suministro_id: string;
  tarifa_codigo: string | null;
}

export async function fetchPerfil(_token: string): Promise<PerfilResponse> {
  return {
    nombre: "Palacios",
    nro_suministro: "2817670",
    suministro_id: "0281767003",
    tarifa_codigo: "140",
  };
}
