import { bg, border, fg, font, fontSize, fontWeight, radius, space } from "../design-tokens";

export interface SelectOpcion {
  value: string;
  label: string;
}

interface Props {
  label: string;
  value: string;
  opciones: SelectOpcion[];
  onChange: (value: string) => void;
}

/** Select estilizado del Design System EPEC (label en mayúsculas + chevron de marca). */
export function SelectControl({ label, value, opciones, onChange }: Props) {
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
        {label}
      </span>
      <select
        aria-label={label}
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
          backgroundImage:    `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23124e2f' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E")`,
          backgroundRepeat:   "no-repeat",
          backgroundPosition: `right ${space[3]}px center`,
        }}
      >
        {opciones.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </label>
  );
}
