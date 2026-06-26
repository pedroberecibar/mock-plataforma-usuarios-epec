// TEMPORARY visual-preview harness for CuentaPage. Delete after screenshot.
import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import { AppShell, type Vista } from "./components/AppShell";
import { CuentaPage } from "./pages/CuentaPage";
import "./index.css";

const CUENTA = {
  personales: {
    nombre_o_razon_social: "María Fernanda López",
    tipo_documento: "DNI",
    nro_documento_masked: "****1815",
    cuit_masked: "********153",
    email: "mf.lopez@example.com",
  },
  suministro: {
    numero: "SRV-2817670",
    estado_servicio: "Activo",
    direccion: "Bv. San Juan 1250 Piso 3 Depto B",
    barrio: "Nueva Córdoba",
    localidad: "Córdoba",
    cp: "5000",
  },
  tarifa: {
    codigo: "140",
    descripcion: "1.a/f RESIDENCIAL",
    grupo_tarifario: "T1",
    clase: "1",
    clase_descripcion: "1 a-b-f Casas de familia",
    tension: "Baja tensión",
  },
  medidor: {
    numero: "CL-0099821",
    marca: "CLOU",
    fase: "Monofásico",
    inteligente_desde: "2023-03-10",
  },
};

// Stub fetch('/cuenta') to return the fixture without backend.
const realFetch = window.fetch.bind(window);
window.fetch = ((input: RequestInfo | URL, init?: RequestInit) => {
  const url = typeof input === "string" ? input : input.toString();
  if (url.includes("/cuenta")) {
    return Promise.resolve(new Response(JSON.stringify(CUENTA), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }));
  }
  return realFetch(input, init);
}) as typeof window.fetch;

function Preview() {
  const [vista, setVista] = useState<Vista>("cuenta");
  return (
    <AppShell vistaActiva={vista} onNavegar={setVista} onLogout={() => {}} usuarioNombre="Mi cuenta">
      <CuentaPage token="preview" />
    </AppShell>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Preview />
  </React.StrictMode>,
);
