import type { ComparacionZonaResponse } from "../api/types";
import {
  cardStyle,
  labelStyle,
  captionStyle,
  color,
  font,
  fontSize,
  fontWeight,
  lineHeight,
  space,
  fg,
} from "../design-tokens";

interface Props {
  zona: ComparacionZonaResponse;
}

export function BloqueZona({ zona }: Props) {
  const { promedio_vecinos_kwh, n_vecinos, diferencia_pct } = zona;

  if (n_vecinos === 0 || promedio_vecinos_kwh === null) {
    return (
      <section aria-label="comparación de zona" style={cardStyle}>
        <p style={labelStyle}>Comparación con tu zona</p>
        <p
          style={{
            ...captionStyle,
            marginTop: space[1],
          }}
        >
          Sin datos de zona disponibles
        </p>
      </section>
    );
  }

  const sube       = diferencia_pct !== null && diferencia_pct > 0;
  const numColor   = sube ? color.error   : color.success;
  const signo      = diferencia_pct !== null && diferencia_pct > 0 ? "+" : "";
  const vecText    = n_vecinos === 1 ? "vecino" : "vecinos";

  return (
    <section aria-label="comparación de zona" style={cardStyle}>
      <p style={labelStyle}>
        Comparación con tu zona ({n_vecinos} {vecText})
      </p>

      {diferencia_pct !== null ? (
        <p
          style={{
            fontFamily:  font.technical,
            fontSize:    fontSize.xl,
            fontWeight:  fontWeight.bold,
            color:       numColor,
            lineHeight:  lineHeight.tight,
            margin:      0,
            marginBottom: space[2],
          }}
        >
          {signo}{diferencia_pct.toFixed(1)}%{" "}
          <span
            style={{
              fontFamily: font.sans,
              fontSize:   fontSize.sm,
              fontWeight: fontWeight.regular,
              color:      fg.secondary,
            }}
          >
            {sube ? "por encima" : "por debajo"} de tu zona
          </span>
        </p>
      ) : (
        <p
          style={{
            fontFamily: font.sans,
            fontSize:   fontSize.sm,
            color:      fg.muted,
            margin:     0,
            marginBottom: space[2],
          }}
        >
          Sin datos suficientes para comparar
        </p>
      )}

      <p
        style={{
          ...captionStyle,
          marginTop: space[1],
        }}
      >
        Promedio zonal: {promedio_vecinos_kwh.toFixed(1)} kWh
      </p>
    </section>
  );
}
