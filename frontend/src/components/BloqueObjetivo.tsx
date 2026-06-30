import type { CSSProperties } from "react";
import type { ObjetivoEstadoResponse } from "../api/types";
import type { Vista } from "./AppShell";
import { resumenObjetivo, semaforoDeObjetivo, type NivelObjetivo } from "../utils/objetivo";
import {
  cardFeaturedStyle,
  color,
  fg,
  font,
  fontSize,
  fontWeight,
  labelStyle,
  lineHeight,
  radius,
  space,
} from "../design-tokens";

interface Props {
  estado: ObjetivoEstadoResponse | null;
  onNavegar?: (vista: Vista) => void;
}

const NIVEL_COLOR: Record<NivelObjetivo, { text: string; bg: string }> = {
  bien:         { text: color.successDark, bg: color.green100 },
  aviso:        { text: color.warningDark, bg: color.warningLight },
  superado:     { text: color.errorDark,   bg: color.errorLight },
  sin_objetivo: { text: fg.muted,          bg: "rgba(140,122,99,0.12)" },
};

function diasDelMesActual(): number {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
}

export function BloqueObjetivo({ estado, onNavegar }: Props) {
  const sinObjetivo =
    !estado || estado.texto_dinamico === "sin_objetivo" || estado.objetivo_kwh == null;

  if (sinObjetivo) {
    return (
      <section aria-label="objetivo del mes" style={cardFeaturedStyle}>
        <p style={labelStyle}>Objetivo del mes</p>
        <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.md, color: fg.muted }}>
          Sin objetivo definido
        </p>
        <p style={{
          margin:     `${space[3]}px 0 ${space[5]}px`,
          fontSize:   fontSize.sm,
          color:      fg.secondary,
          lineHeight: lineHeight.relaxed,
        }}>
          Definí una meta mensual para ver tu ritmo de consumo.
        </p>
        <button onClick={() => onNavegar?.("objetivos")} style={ctaStyle}>
          Definí tu objetivo
        </button>
      </section>
    );
  }

  const sem = semaforoDeObjetivo(estado.texto_dinamico);
  const c = NIVEL_COLOR[sem.nivel];
  const { kwhRestantes, kwhPorDia, diasRestantes } = resumenObjetivo(estado, diasDelMesActual());

  return (
    <section aria-label="objetivo del mes" style={cardFeaturedStyle}>
      <p style={labelStyle}>Objetivo del mes</p>

      <span style={{
        display:      "inline-block",
        marginTop:    space[1],
        marginBottom: space[3],
        padding:      `${space[1]}px ${space[3]}px`,
        borderRadius: radius.full,
        background:   c.bg,
        color:        c.text,
        fontSize:     fontSize.sm,
        fontWeight:   fontWeight.semibold,
      }}>
        {sem.label}
      </span>

      <p style={{
        fontFamily:    font.technical,
        fontSize:      fontSize["4xl"],
        fontWeight:    fontWeight.light,
        color:         fg.link,
        lineHeight:    lineHeight.tight,
        margin:        0,
        letterSpacing: "-0.02em",
      }}>
        {kwhRestantes != null ? Math.round(kwhRestantes) : "—"}
        <span style={{
          fontFamily: font.sans,
          fontSize:   fontSize.xl,
          fontWeight: fontWeight.light,
          color:      fg.secondary,
          marginLeft: space[2],
        }}>
          kWh restantes
        </span>
      </p>

      {kwhPorDia != null && (
        <p style={{ margin: `${space[3]}px 0 0`, fontSize: fontSize.xs, color: fg.muted }}>
          Podés usar ~{Math.round(kwhPorDia)} kWh/día los {diasRestantes} días que quedan.
        </p>
      )}

      <div style={{ marginTop: space[4] }}>
        <button onClick={() => onNavegar?.("objetivos")} style={linkStyle}>
          Ver detalle →
        </button>
      </div>
    </section>
  );
}

const ctaStyle: CSSProperties = {
  padding:      `${space[3]}px ${space[5]}px`,
  background:   color.green700,
  color:        fg.onDark,
  border:       "none",
  borderRadius: radius.md,
  fontSize:     fontSize.sm,
  fontWeight:   fontWeight.semibold,
  fontFamily:   font.sans,
  cursor:       "pointer",
};

const linkStyle: CSSProperties = {
  background:  "none",
  border:      "none",
  padding:     0,
  color:       fg.link,
  fontFamily:  font.sans,
  fontSize:    fontSize.sm,
  fontWeight:  fontWeight.semibold,
  cursor:      "pointer",
};
