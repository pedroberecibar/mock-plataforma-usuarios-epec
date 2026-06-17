import { useEffect, useState } from "react";
import type { HomeResponse } from "../api/types";
import { fetchHome } from "../api/home";
import { BloqueConsumoMes } from "../components/BloqueConsumoMes";
import { BloqueZona } from "../components/BloqueZona";
import { BloqueProyeccion } from "../components/BloqueProyeccion";
import { BloqueAccesos } from "../components/BloqueAccesos";
import {
  bg,
  fg,
  font,
  fontSize,
  fontWeight,
  space,
  color,
  shadow,
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
}

export function HomePage({ token, suministroId, mes }: Props) {
  const [data, setData] = useState<HomeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const mesStr = mes ?? mesActualYYYYMM();

  useEffect(() => {
    setLoading(true);
    fetchHome(token, suministroId, mesStr)
      .then(setData)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Error desconocido")
      )
      .finally(() => setLoading(false));
  }, [token, suministroId, mesStr]);

  if (loading) {
    return (
      <div
        style={{
          minHeight:      "100vh",
          background:     bg.page,
          display:        "flex",
          alignItems:     "center",
          justifyContent: "center",
          fontFamily:     font.sans,
          fontSize:       fontSize.sm,
          color:          fg.muted,
        }}
      >
        Cargando...
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          minHeight:  "100vh",
          background: bg.page,
          display:    "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: font.sans,
        }}
      >
        <p
          role="alert"
          style={{
            background:   color.errorLight,
            color:        color.errorDark,
            border:       `1px solid ${color.error}`,
            borderRadius: 4,
            padding:      `${space[3]}px ${space[4]}px`,
            fontSize:     fontSize.sm,
            margin:       0,
          }}
        >
          Error: {error}
        </p>
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
    <div
      style={{
        minHeight:  "100vh",
        background: bg.page,
        fontFamily: font.sans,
      }}
    >
      {/* Header */}
      <header
        style={{
          background:  bg.header,
          boxShadow:   shadow.sm,
          position:    "sticky" as const,
          top:         0,
          zIndex:      100,
        }}
      >
        <div
          style={{
            maxWidth: 960,
            margin:   "0 auto",
            padding:  `${space[3]}px ${space[6]}px`,
            display:  "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <img
            src="/epec-logo-white.png"
            alt="EPEC"
            style={{ height: 32 }}
            onError={(e) => {
              // Fallback: mostrar texto si el logo no carga
              (e.currentTarget as HTMLImageElement).style.display = "none";
              const next = e.currentTarget.nextElementSibling as HTMLElement | null;
              if (next) next.style.display = "block";
            }}
          />
          <span
            style={{
              display:    "none",
              fontFamily: font.sans,
              fontSize:   fontSize.md,
              fontWeight: fontWeight.bold,
              color:      fg.onDark,
              letterSpacing: "0.04em",
            }}
          >
            EPEC
          </span>

          <span
            style={{
              fontFamily: font.sans,
              fontSize:   fontSize.xs,
              color:      color.green200,
              letterSpacing: "0.04em",
            }}
          >
            Plataforma de Clientes
          </span>
        </div>
      </header>

      {/* Main content */}
      <main aria-label="home del cliente">
        <div
          style={{
            maxWidth: 960,
            margin:   "0 auto",
            padding:  `${space[8]}px ${space[6]}px`,
          }}
        >
          {/* 2-column grid on wide, stack on narrow */}
          <div
            style={{
              display:             "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap:                 space[6],
            }}
          >
            <BloqueConsumoMes consumoMes={data.consumo_mes} />
            <BloqueZona zona={data.comparacion_zona} />
            <BloqueProyeccion proyeccion={data.proyeccion} />
            <BloqueAccesos suministroId={suministroId} />
          </div>

          {/* Timestamp footer */}
          <p
            style={{
              fontFamily:  font.sans,
              fontSize:    fontSize.xs,
              color:       fg.muted,
              marginTop:   space[6],
              marginBottom: 0,
              textAlign:   "right" as const,
            }}
          >
            Actualizado: {tsDate}
          </p>
        </div>
      </main>
    </div>
  );
}
