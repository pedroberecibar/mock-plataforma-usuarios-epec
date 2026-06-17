import { ConsumoPage } from "./pages/ConsumoPage";
import { HomePage } from "./pages/HomePage";

// Para el MVP: token y suministro hardcodeados temporalmente.
// En producción se leen de localStorage / contexto de autenticación.
const DEMO_TOKEN = import.meta.env.VITE_DEMO_TOKEN ?? "";
const DEMO_SUMINISTRO = import.meta.env.VITE_DEMO_SUMINISTRO ?? "SRV-91013496";

const VISTA = import.meta.env.VITE_VISTA ?? "home"; // "home" | "consumo"

function App() {
  if (VISTA === "consumo") {
    return <ConsumoPage token={DEMO_TOKEN} suministroId={DEMO_SUMINISTRO} />;
  }
  return <HomePage token={DEMO_TOKEN} suministroId={DEMO_SUMINISTRO} />;
}

export default App;
