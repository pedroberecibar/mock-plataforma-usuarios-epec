import { useState } from "react";
import { AppShell, type Vista } from "./components/AppShell";
import type { AuthState } from "./hooks/auth";
import { getAuthState, saveAuthState } from "./hooks/auth";
import { LoginPage } from "./pages/LoginPage";
import { AlertasPage } from "./pages/AlertasPage";
import { ConsumoPage } from "./pages/ConsumoPage";
import { FacturaPage } from "./pages/FacturaPage";
import { HomePage } from "./pages/HomePage";

function App() {
  const [auth, setAuth] = useState<AuthState | null>(getAuthState);
  const [vista, setVista] = useState<Vista>("home");

  function handleLogin(state: AuthState) {
    saveAuthState(state);
    setAuth(state);
  }

  if (!auth) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <AppShell vistaActiva={vista} onNavegar={setVista} usuarioNombre="Mi cuenta">
      {vista === "home" && <HomePage token={auth.token} suministroId={auth.suministroId} />}
      {vista === "consumo" && <ConsumoPage token={auth.token} suministroId={auth.suministroId} />}
      {vista === "factura" && <FacturaPage token={auth.token} />}
      {vista === "alertas" && <AlertasPage token={auth.token} />}
    </AppShell>
  );
}

export default App;
