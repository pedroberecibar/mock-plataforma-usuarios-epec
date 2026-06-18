export interface LoginResponse {
  token: string;
  suministro_id: string;
}

export async function postLogin(usuario: string, password: string): Promise<LoginResponse> {
  const resp = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ usuario, password }),
  });
  if (!resp.ok) throw new Error("Credenciales inválidas");
  return resp.json() as Promise<LoginResponse>;
}
