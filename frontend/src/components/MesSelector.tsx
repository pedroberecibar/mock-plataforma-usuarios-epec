import { bg, border, fg, font, fontSize, fontWeight, radius, space } from "../design-tokens";
import type { MesOpcion } from "../utils/meses";

interface Props {
  value: string;
  meses: MesOpcion[];
  onChange: (value: string) => void;
}

export function MesSelector({ value, meses, onChange }: Props) {
  return (
    <label style={{ display: "inline-flex", alignItems: "center", gap: space[2] }}>
      <span style={{
        fontSize:      fontSize.xs,
        fontWeight:    fontWeight.semibold,
        color:         fg.secondary,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        fontFamily:    font.sans,
      }}>
        Mes
      </span>
      <select
        aria-label="Mes"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          appearance:   "none",
          background:   bg.surface,
          border:       `1px solid ${border.default}`,
          borderRadius: radius.sm,
          color:        fg.primary,
          fontFamily:   font.sans,
          fontSize:     fontSize.sm,
          fontWeight:   fontWeight.medium,
          padding:      `${space[2]}px ${space[8]}px ${space[2]}px ${space[3]}px`,
          cursor:       "pointer",
          outline:      "none",
          // chevron dibujado con background (sin libs) usando el verde de marca
          backgroundImage:    `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23124e2f' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E")`,
          backgroundRepeat:   "no-repeat",
          backgroundPosition: `right ${space[3]}px center`,
        }}
      >
        {meses.map((m) => (
          <option key={m.value} value={m.value}>{m.label}</option>
        ))}
      </select>
    </label>
  );
}
