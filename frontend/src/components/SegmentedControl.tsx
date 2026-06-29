import { bg, border, brand, fg, font, fontSize, fontWeight, radius, space } from "../design-tokens";

export interface SegmentedOpcion {
  value: string;
  label: string;
}

interface Props {
  value: string;
  opciones: SegmentedOpcion[];
  onChange: (value: string) => void;
  ariaLabel: string;
}

/**
 * Control segmentado tipo "pill" alineado al Design System EPEC:
 * contenedor cálido con la opción activa en verde de marca.
 */
export function SegmentedControl({ value, opciones, onChange, ariaLabel }: Props) {
  return (
    <div
      role="group"
      aria-label={ariaLabel}
      style={{
        display:      "inline-flex",
        gap:          space[1],
        padding:      space[1],
        background:   bg.surface,
        border:       `1px solid ${border.default}`,
        borderRadius: radius.full,
      }}
    >
      {opciones.map((op) => {
        const activo = op.value === value;
        return (
          <button
            key={op.value}
            type="button"
            aria-pressed={activo}
            onClick={() => { if (!activo) onChange(op.value); }}
            style={{
              border:       "none",
              cursor:       activo ? "default" : "pointer",
              padding:      `${space[2]}px ${space[4]}px`,
              borderRadius: radius.full,
              fontFamily:   font.sans,
              fontSize:     fontSize.sm,
              fontWeight:   fontWeight.semibold,
              background:   activo ? brand.primary : "transparent",
              color:        activo ? fg.onDark : fg.secondary,
              transition:   "background 150ms ease, color 150ms ease",
              whiteSpace:   "nowrap",
            }}
          >
            {op.label}
          </button>
        );
      })}
    </div>
  );
}
