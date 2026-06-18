const KEY = "epec_auth";

export interface AuthState {
  token: string;
  suministroId: string;
}

export function getAuthState(): AuthState | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    return JSON.parse(raw) as AuthState;
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
