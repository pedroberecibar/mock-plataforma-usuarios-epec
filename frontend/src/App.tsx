import { useState } from "react";
import { AppShell, type Vista } from "./components/AppShell";
import type { AuthState } from "./hooks/auth";
import { clearAuthState, getAuthState, saveAuthState } from "./hooks/auth";
import { LoginPage } from "./pages/LoginPage";
import { AlertasPage } from "./pages/AlertasPage";
import { ConsumoPage } from "./pages/ConsumoPage";
import { FacturaPage } from "./pages/FacturaPage";
import { HomePage } from "./pages/HomePage";
import { ObjetivosPage } from "./pages/ObjetivosPage";

function App() {
  const [auth, setAuth] = useState<AuthState | null>(getAuthState);
  const [vista, setVista] = useState<Vista>("home");

  function handleLogin(state: AuthState) {
    saveAuthState(state);
    setAuth(state);
  }

  function handleLogout() {
    clearAuthState();
    setAuth(null);
  }

  if (!auth) {
    return <LoginPage onLogin={handleLogin} />;
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
