import { fg, font, fontWeight } from "../design-tokens";

type Variant = "hero" | "card" | "inline";

interface Props {
  value: number;
  sublabel?: string;
  variant?: Variant;
  color?: string;
  decimals?: number;
}

const FONT_SIZE: Record<Variant, number> = {
  hero:   42,
  card:   28,
  inline: 24,
};

const FONT_WEIGHT: Record<Variant, number> = {
  hero:   fontWeight.light,
  card:   fontWeight.regular,
  inline: fontWeight.medium,
};

export function KwhHero({
  value,
  sublabel,
  variant = "hero",
  color: colorProp,
  decimals = 0,
}: Props) {
  const formattedValue = value.toLocaleString("es-AR", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  const textColor = colorProp ?? fg.primary;
  const unitSize = Math.round(FONT_SIZE[variant] * 0.45);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
        <span
          data-testid="kwh-value"
          style={{
            fontFamily:  font.technical,
            fontSize:    FONT_SIZE[variant],
            fontWeight:  FONT_WEIGHT[variant],
            color:       textColor,
            lineHeight:  1,
            letterSpacing: "-0.01em",
          }}
        >
          {formattedValue}
        </span>
        <span
          style={{
            fontFamily: font.sans,
            fontSize:   unitSize,
            fontWeight: fontWeight.regular,
            color:      fg.muted,
            lineHeight: 1,
          }}
        >
          kWh
        </span>
      </div>
      {sublabel && (
        <p
          data-testid="kwh-sublabel"
          style={{
            fontFamily: font.sans,
            fontSize:   12,
            color:      fg.muted,
            margin:     0,
            lineHeight: 1.4,
          }}
        >
          {sublabel}
        </p>
      )}
    </div>
  );
}
