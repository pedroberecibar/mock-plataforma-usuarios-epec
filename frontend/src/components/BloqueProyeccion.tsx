import type { ProyeccionResponse } from "../api/types";
import {
  cardStyle,
  labelStyle,
  captionStyle,
  color,
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
  alta:      { background: color.successLight, color: color.successDark },
  media:     { background: color.warningLight, color: color.warningDark },
  baja:      { background: color.errorLight,   color: color.errorDark   },
  sin_datos: { background: color.neutral100,   color: color.neutral600  },
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
      <section aria-label="proyección mensual" style={cardStyle}>
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
    <section aria-label="proyección mensual" style={cardStyle}>
      <p style={labelStyle}>Proyección del mes</p>

      <p
        style={{
          fontFamily:  font.technical,
          fontSize:    fontSize.xl,
          fontWeight:  fontWeight.bold,
          color:       fg.primary,
          lineHeight:  lineHeight.tight,
          margin:      0,
          marginBottom: space[2],
        }}
      >
        {rango_inferior_kwh.toFixed(0)} – {rango_superior_kwh.toFixed(0)}{" "}
        <span
          style={{
            fontFamily: font.sans,
            fontSize:   fontSize.sm,
            fontWeight: fontWeight.regular,
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
