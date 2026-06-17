import { useState } from "react";
import { AppShell, type Vista } from "./components/AppShell";
import { ConsumoPage } from "./pages/ConsumoPage";
import { HomePage } from "./pages/HomePage";

// For MVP: token and suministro hardcoded temporarily.
// In production these come from localStorage / auth context.
const DEMO_TOKEN = import.meta.env.VITE_DEMO_TOKEN ?? "";
const DEMO_SUMINISTRO = import.meta.env.VITE_DEMO_SUMINISTRO ?? "SRV-91013496";

function App() {
  const [vista, setVista] = useState<Vista>("home");

  return (
    <AppShell vistaActiva={vista} onNavegar={setVista} usuarioNombre="Pedro Berecibar">
      {vista === "home" && <HomePage token={DEMO_TOKEN} suministroId={DEMO_SUMINISTRO} />}
      {vista === "consumo" && <ConsumoPage token={DEMO_TOKEN} suministroId={DEMO_SUMINISTRO} />}
    </AppShell>
  );
}

export default App;
