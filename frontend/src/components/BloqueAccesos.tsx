import {
  cardStyle,
  labelStyle,
  brand,
  color,
  font,
  fontSize,
  fontWeight,
  radius,
  space,
} from "../design-tokens";
import type { Vista } from "./AppShell";

interface AccesoItem {
  label: string;
  vista: Vista;
}

const ACCESOS: AccesoItem[] = [
  { label: "Mi Consumo",  vista: "consumo" },
  { label: "Mi Factura",  vista: "factura" },
  { label: "Objetivos",   vista: "objetivos" },
  { label: "Alertas",     vista: "alertas" },
];

interface Props {
  suministroId: string;
  onNavegar?: (vista: Vista) => void;
}

export function BloqueAccesos({ onNavegar }: Props) {
  return (
    <section aria-label="accesos rápidos" style={cardStyle}>
      <p style={labelStyle}>Accesos rápidos</p>
      <div style={{
        display:        "grid",
        gridTemplateColumns: "1fr 1fr",
        gap:            space[2],
        marginTop:      space[3],
      }}>
        {ACCESOS.map(({ label, vista }) => (
          <button
            key={vista}
            onClick={() => onNavegar?.(vista)}
            style={{
              display:      "block",
              width:        "100%",
              padding:      `${space[3]}px ${space[4]}px`,
              background:   brand.primary,
              color:        color.white,
              border:       "none",
              borderRadius: radius.md,
              fontSize:     fontSize.sm,
              fontWeight:   fontWeight.semibold,
              fontFamily:   font.sans,
              cursor:       "pointer",
              textAlign:    "center" as const,
              transition:   "background 150ms ease",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = brand.hover;
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = brand.primary;
            }}
          >
            {label}
          </button>
        ))}
      </div>
    </section>
  );
}
