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
        minHeight:  "100%",
        background: bg.page,
        fontFamily: font.sans,
      }}
    >
      {/* Content header (top app bar style, sticky) */}
      <header style={{
        height:           64,
        display:          "flex",
        justifyContent:   "space-between",
        alignItems:       "flex-start",
        padding:          `${space[6]}px ${space[10]}px`,
        background:       bg.page,
        borderBottom:     `1px solid ${border.default}`,
        position:         "sticky",
        top:              0,
        zIndex:           40,
      }}>
        <div>
          <h2 style={{
            fontFamily:   font.sans,
            fontSize:     fontSize["2xl"],
            fontWeight:   fontWeight.semibold,
            color:        fg.link,
            margin:       0,
            letterSpacing: "-0.01em",
            lineHeight:   1.25,
          }}>
            Inicio
          </h2>
        </div>
      </header>

      <main aria-label="home del cliente">
        <div
          style={{
            maxWidth: 1400,
            padding:  `${space[10]}px ${space[10]}px`,
          }}
        >
          {/* 2-column grid on wide, stack on narrow */}
          <div
            style={{
              display:             "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
              gap:                 space[6],
            }}
          >
            <BloqueConsumoMes consumoMes={data.consumo_mes} />
            <BloqueZona zona={data.comparacion_zona} />
            <BloqueProyeccion proyeccion={data.proyeccion} />
            <BloqueAccesos suministroId={suministroId} />
          </div>

          {/* Timestamp footer */}
          <footer style={{
            marginTop:    space[10],
            paddingTop:   space[6],
            borderTop:    `1px solid ${border.default}`,
            display:      "flex",
            justifyContent: "flex-end",
          }}>
            <p
              style={{
                fontFamily:   font.mono,
                fontSize:     fontSize.xs,
                letterSpacing: "0.05em",
                color:        fg.muted,
                margin:       0,
              }}
            >
              Actualizado: {tsDate}
            </p>
          </footer>
        </div>
      </main>
    </div>
  );
}
