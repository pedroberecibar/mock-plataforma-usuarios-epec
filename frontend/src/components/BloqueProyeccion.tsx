import type { ProyeccionResponse } from "../api/types";
import {
  cardFeaturedStyle,
  labelStyle,
  captionStyle,
  font,
  fontSize,
  fontWeight,
  lineHeight,
  radius,
  space,
  fg,
} from "../design-tokens";

interface Props {
  proyeccion: ProyeccionResponse;
}

type ConfianzaKey = "alta" | "media" | "baja" | "sin_datos";

const CONFIANZA_LABEL: Record<ConfianzaKey, string> = {
  alta:      "Alta confianza",
  media:     "Confianza media",
  baja:      "Baja confianza",
  sin_datos: "Sin datos",
};

interface BadgeStyle {
  background: string;
  color: string;
}

const CONFIANZA_BADGE: Record<ConfianzaKey, BadgeStyle> = {
  alta:      { background: "rgba(18,78,47,0.10)",   color: "#155a2e" },
  media:     { background: "rgba(230,145,10,0.10)", color: "#7a4a00" },
  baja:      { background: "rgba(230,145,10,0.10)", color: "#7a4a00" },
  sin_datos: { background: "#F3EDE2",               color: "#6B5A45" },
};

function ConfianzaBadge({ bandera }: { bandera: string }) {
  const key = (bandera in CONFIANZA_BADGE ? bandera : "sin_datos") as ConfianzaKey;
  const { background, color: textColor } = CONFIANZA_BADGE[key];
  const label = CONFIANZA_LABEL[key] ?? bandera;

  return (
    <span
      style={{
        display:      "inline-block",
        background,
        color:        textColor,
        borderRadius: radius.xs,
        padding:      `${space[1]}px ${space[2]}px`,
        fontSize:     fontSize.xs,
        fontWeight:   fontWeight.semibold,
        fontFamily:   font.sans,
        lineHeight:   lineHeight.normal,
      }}
    >
      {label}
    </span>
  );
}

export function BloqueProyeccion({ proyeccion }: Props) {
  const { metodo_aplicado, bandera_confianza, rango_inferior_kwh, rango_superior_kwh } = proyeccion;

  if (metodo_aplicado === "insuficiente" || rango_inferior_kwh === null || rango_superior_kwh === null) {
    return (
      <section aria-label="proyección mensual" style={cardFeaturedStyle}>
        <p style={labelStyle}>Proyección del mes</p>
        <p
          style={{
            fontFamily:  font.sans,
            fontSize:    fontSize.sm,
            color:       fg.muted,
            margin:      0,
            marginBottom: space[1],
          }}
        >
          Datos insuficientes para proyectar
        </p>
        <p style={{ ...captionStyle, marginTop: space[1] }}>
          Se necesitan al menos 7 días de datos
        </p>
      </section>
    );
  }

  return (
    <section aria-label="proyección mensual" style={cardFeaturedStyle}>
      <p style={labelStyle}>Proyección del mes</p>

      <p
        style={{
          fontFamily:    font.technical,
          fontSize:      fontSize["4xl"],  // 48px — hero kWh display
          fontWeight:    fontWeight.light, // 300 — elegante, no pesado
          color:         fg.link,          // #124e2f
          lineHeight:    lineHeight.tight,
          margin:        0,
          marginBottom:  space[2],
          letterSpacing: "-0.02em",
        }}
      >
        {rango_inferior_kwh.toFixed(0)} – {rango_superior_kwh.toFixed(0)}{" "}
        <span
          style={{
            fontFamily: font.sans,
            fontSize:   fontSize.xl,    // unit-display: 24px
            fontWeight: fontWeight.light,  // 300
            color:      fg.secondary,
          }}
        >
          kWh
        </span>
      </p>

      <div style={{ marginBottom: space[2] }}>
        <ConfianzaBadge bandera={bandera_confianza} />
      </div>

      <p style={captionStyle}>
        Se ajusta a medida que avanza el mes
      </p>
    </section>
  );
}
