const KEY = "epec_auth";

export interface AuthState {
  token: string;
  suministroId: string;
  nombre: string | null;
  nroSuministro: string;
}

export function getAuthState(): AuthState | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<AuthState>;
    if (!parsed.token || !parsed.suministroId) return null;
    return {
      token: parsed.token,
      suministroId: parsed.suministroId,
      nombre: parsed.nombre ?? null,
      nroSuministro: parsed.nroSuministro ?? parsed.suministroId,
    };
  } catch {
    return null;
  }
}

export function saveAuthState(state: AuthState): void {
  localStorage.setItem(KEY, JSON.stringify(state));
}

export function clearAuthState(): void {
  localStorage.removeItem(KEY);
}
