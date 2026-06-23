import type { ConsumoMesResponse } from "../api/types";
import {
  cardFeaturedStyle,
  labelStyle,
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
  consumoMes: ConsumoMesResponse;
}

interface DeltaChipProps {
  value: number | null;
  label: string;
}

function DeltaChip({ value, label }: DeltaChipProps) {
  if (value === null) {
    return (
      <span
        style={{
          fontFamily:   font.sans,
          fontSize:     fontSize.xs,
          color:        fg.muted,
          background:   "rgba(180,170,155,0.25)",
          borderRadius: radius.xs,
          padding:      `${space[1]}px ${space[2]}px`,
          fontWeight:   fontWeight.medium,
          lineHeight:   lineHeight.normal,
        }}
      >
        {label}: s/d
      </span>
    );
  }

  const sube      = value > 0;
  const chipBg    = sube ? "rgba(192,57,43,0.08)"  : "rgba(18,78,47,0.10)";
  const chipColor = sube ? color.errorDark          : color.successDark;
  const arrow     = sube ? "▲" : "▼";

  return (
    <span
      style={{
        display:    "inline-flex",
        alignItems: "center",
        gap:        3,
        background: chipBg,
        color:      chipColor,
        borderRadius: radius.xs,
        padding:    `${space[1]}px ${space[2]}px`,
        fontSize:   fontSize.xs,
        fontWeight: fontWeight.semibold,
        fontFamily: font.sans,
        lineHeight: lineHeight.normal,
        whiteSpace: "nowrap",
      }}
    >
      {arrow} {Math.abs(value).toFixed(1)}% {label}
    </span>
  );
}

export function BloqueConsumoMes({ consumoMes }: Props) {
  const { total_kwh, vs_mes_anterior_pct, vs_anio_anterior_pct } = consumoMes;

  return (
    <section aria-label="consumo del mes" style={cardFeaturedStyle}>
      <p style={labelStyle}>Consumo este mes</p>

      <p
        style={{
          fontFamily:    font.technical,
          fontSize:      fontSize["4xl"],
          fontWeight:    fontWeight.light,
          color:         fg.link,
          lineHeight:    lineHeight.tight,
          margin:        0,
          marginBottom:  space[3],
          letterSpacing: "-0.02em",
        }}
      >
        {total_kwh !== null ? total_kwh.toFixed(1) : "—"}
        <span
          style={{
            fontFamily: font.sans,
            fontSize:   fontSize.xl,
            fontWeight: fontWeight.light,
            color:      fg.secondary,
            marginLeft: space[2],
          }}
        >
          kWh
        </span>
      </p>

      <div style={{ display: "flex", gap: space[2], flexWrap: "wrap" as const }}>
        <DeltaChip value={vs_mes_anterior_pct} label="vs mes anterior" />
        <DeltaChip value={vs_anio_anterior_pct} label="vs año anterior" />
      </div>
    </section>
  );
}
