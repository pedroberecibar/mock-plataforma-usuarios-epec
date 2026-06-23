import { useEffect, useState } from "react";
import type { HomeResponse } from "../api/types";
import { fetchHome } from "../api/home";
import { BloqueConsumoMes } from "../components/BloqueConsumoMes";
import { BloqueZona } from "../components/BloqueZona";
import { BloqueProyeccion } from "../components/BloqueProyeccion";
import { BloqueAccesos } from "../components/BloqueAccesos";
import { PageHeader } from "../components/PageHeader";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { AlertBanner } from "../components/AlertBanner";
import type { Vista } from "../components/AppShell";
import {
  bg,
  fg,
  font,
  fontSize,
  space,
  border,
} from "../design-tokens";

function mesActualYYYYMM(): string {
  const now = new Date();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  return `${now.getFullYear()}-${m}`;
}

interface Props {
  token: string;
  suministroId: string;
  mes?: string;
  onNavegar?: (vista: Vista) => void;
}

export function HomePage({ token, suministroId, mes, onNavegar }: Props) {
  const [data, setData] = useState<HomeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const mesStr = mes ?? mesActualYYYYMM();

  useEffect(() => {
    setLoading(true);
    fetchHome(token, mesStr)
      .then(setData)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Error desconocido")
      )
      .finally(() => setLoading(false));
  }, [token, suministroId, mesStr]);

  if (loading) {
    return (
      <div style={{ background: bg.page, minHeight: "100%" }}>
        <PageHeader title="Inicio" />
        <div style={{ padding: `${space[10]}px`, maxWidth: 1400, margin: "0 auto" }}>
          <div style={{
            display:             "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap:                 space[6],
          }}>
            <LoadingSkeleton variant="card" />
            <LoadingSkeleton variant="card" />
            <LoadingSkeleton variant="card" />
            <LoadingSkeleton variant="card" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: bg.page, minHeight: "100%" }}>
        <PageHeader title="Inicio" />
        <div style={{ padding: `${space[10]}px`, maxWidth: 1400, margin: "0 auto" }}>
          <AlertBanner variant="error">Error al cargar: {error}</AlertBanner>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const tsDate = new Date(data.timestamp).toLocaleString("es-AR", {
    timeZone:  "America/Argentina/Cordoba",
    day:       "numeric",
    month:     "short",
    hour:      "2-digit",
    minute:    "2-digit",
  });

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <PageHeader title="Inicio" />

      <main aria-label="home del cliente">
        <div style={{
          maxWidth: 1400,
          margin:   "0 auto",
          padding:  `${space[10]}px`,
        }}>
          <div style={{
            display:             "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap:                 space[6],
          }}>
            <BloqueConsumoMes consumoMes={data.consumo_mes} />
            <BloqueZona zona={data.comparacion_zona} />
            <BloqueProyeccion proyeccion={data.proyeccion} />
            <BloqueAccesos suministroId={suministroId} onNavegar={onNavegar} />
          </div>

          <footer style={{
            marginTop:      space[10],
            paddingTop:     space[6],
            borderTop:      `1px solid ${border.default}`,
            display:        "flex",
            justifyContent: "flex-end",
          }}>
            <p style={{
              fontFamily:    font.mono,
              fontSize:      fontSize.xs,
              letterSpacing: "0.05em",
              color:         fg.muted,
              margin:        0,
            }}>
              Actualizado: {tsDate}
            </p>
          </footer>
        </div>
      </main>
    </div>
  );
}
