export interface LoginResponse {
  token: string;
  suministro_id: string;
  nombre: string | null;
  nro_suministro: string;
}

export async function postLogin(
  _usuario: string,
  _password: string
): Promise<LoginResponse> {
  return {
    token: "demo-token",
    suministro_id: "0281767003",
    nombre: "Palacios",
    nro_suministro: "2817670",
  };
}
