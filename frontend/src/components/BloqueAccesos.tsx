import type React from "react";
import {
  cardStyle,
  labelStyle,
  brand,
  color,
  font,
  fontSize,
  fontWeight,
  lineHeight,
  radius,
  space,
  fg,
  border,
} from "../design-tokens";

interface Props {
  suministroId: string;
}

interface BtnPrimaryStyle extends React.CSSProperties {
  // typed so hover is handled via onMouseEnter/onMouseLeave
}

const btnBase: React.CSSProperties = {
  display:      "inline-block",
  padding:      `${space[2] + 2}px ${space[5]}px`,
  borderRadius: radius.sm,
  fontSize:     fontSize.sm,
  fontWeight:   fontWeight.medium,
  fontFamily:   font.sans,
  lineHeight:   lineHeight.normal,
  cursor:       "pointer",
  border:       "none",
  textDecoration: "none",
  transition:   "background 150ms ease",
};

const btnPrimary: BtnPrimaryStyle = {
  ...btnBase,
  background: brand.primary,
  color:      color.white,
};

const btnDisabled: React.CSSProperties = {
  ...btnBase,
  background: color.neutral100,
  color:      fg.muted,
  border:     `1px solid ${border.default}`,
  cursor:     "not-allowed",
  opacity:    0.8,
};

export function BloqueAccesos({ suministroId }: Props) {
  const handleMouseEnter = (e: React.MouseEvent<HTMLAnchorElement>) => {
    (e.currentTarget as HTMLAnchorElement).style.background = brand.hover;
  };
  const handleMouseLeave = (e: React.MouseEvent<HTMLAnchorElement>) => {
    (e.currentTarget as HTMLAnchorElement).style.background = brand.primary;
  };

  return (
    <section aria-label="accesos rápidos" style={cardStyle}>
      <p style={labelStyle}>Accesos rápidos</p>
      <div style={{ display: "flex", gap: space[2], flexWrap: "wrap" as const, marginTop: space[3] }}>
        <a
          href={`/consumo?id=${suministroId}`}
          style={btnPrimary}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          Ver consumo detallado
        </a>
        <button
          disabled
          style={btnDisabled}
          aria-disabled="true"
        >
          Mi factura (próximamente)
        </button>
        <button
          disabled
          style={btnDisabled}
          aria-disabled="true"
        >
          Alertas (próximamente)
        </button>
      </div>
    </section>
  );
}
