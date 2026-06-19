import { useEffect, useState } from "react";
import { AppShell, type Vista } from "./components/AppShell";
import type { AuthState } from "./hooks/auth";
import { clearAuthState, getAuthState, saveAuthState } from "./hooks/auth";
import { fetchObjetivo, type ObjetivoResponse } from "./api/objetivos";
import { LoginPage } from "./pages/LoginPage";
import { AlertasPage } from "./pages/AlertasPage";
import { ConsumoPage } from "./pages/ConsumoPage";
import { FacturaPage } from "./pages/FacturaPage";
import { HomePage } from "./pages/HomePage";
import { ObjetivosPage } from "./pages/ObjetivosPage";
import { OnboardingObjetivoPage } from "./pages/OnboardingObjetivoPage";

function App() {
  const [auth, setAuth] = useState<AuthState | null>(getAuthState);
  const [vista, setVista] = useState<Vista>("home");
  const [onboarding, setOnboarding] = useState<boolean | null>(null); // null = no verificado aún

  useEffect(() => {
    if (!auth) return;
    fetchObjetivo(auth.token)
      .then((obj) => setOnboarding(obj === null))
      .catch(() => setOnboarding(false)); // si falla, no bloquear
  }, [auth]);

  function handleLogin(state: AuthState) {
    saveAuthState(state);
    setAuth(state);
    setOnboarding(null);
  }

  function handleLogout() {
    clearAuthState();
    setAuth(null);
    setOnboarding(null);
  }

  function handleObjetivoGuardado(_: ObjetivoResponse) {
    setOnboarding(false);
    setVista("home");
  }

  if (!auth) {
    return <LoginPage onLogin={handleLogin} />;
  }

  if (onboarding === null) {
    return null; // verificando — evita flash
  }

  if (onboarding) {
    return (
      <OnboardingObjetivoPage
        token={auth.token}
        suministroId={auth.suministroId}
        onObjetivoGuardado={handleObjetivoGuardado}
      />
    );
  }

  return (
    <AppShell vistaActiva={vista} onNavegar={setVista} onLogout={handleLogout} usuarioNombre="Mi cuenta">
      {vista === "home" && <HomePage token={auth.token} suministroId={auth.suministroId} />}
      {vista === "consumo" && <ConsumoPage token={auth.token} suministroId={auth.suministroId} />}
      {vista === "objetivos" && <ObjetivosPage token={auth.token} suministroId={auth.suministroId} />}
      {vista === "factura" && <FacturaPage token={auth.token} />}
      {vista === "alertas" && <AlertasPage token={auth.token} />}
    </AppShell>
  );
}

export default App;
