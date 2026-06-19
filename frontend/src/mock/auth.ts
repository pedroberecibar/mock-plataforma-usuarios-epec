export interface LoginResponse {
  token: string;
  suministro_id: string;
}

export async function postLogin(
  _usuario: string,
  _password: string
): Promise<LoginResponse> {
  return { token: "demo-token", suministro_id: "SRV-91013496" };
}
