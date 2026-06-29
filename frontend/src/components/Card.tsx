import type { CSSProperties, ReactNode } from "react";
import { bg, fg, font, fontSize, fontWeight, radius, shadow, space } from "../design-tokens";

/**
 * Card destacada estándar del Design System EPEC.
 * Misma estética en todas las páginas (Consumo, Objetivos): superficie beige
 * (surfaceFeat), radio lg, sombra sutil y padding generoso.
 */
export function Card({
  children,
  style,
  ariaLabel,
}: {
  children: ReactNode;
  style?: CSSProperties;
  ariaLabel?: string;
}) {
  return (
    <section
      aria-label={ariaLabel}
      style={{
        background:   bg.surfaceFeat,
        borderRadius: `${radius.lg}px`,
        boxShadow:    shadow.sm,
        padding:      `${space[6]}px`,
        fontFamily:   font.sans,
        ...style,
      }}
    >
      {children}
    </section>
  );
}

/** Etiqueta en mayúsculas usada como encabezado de card / stat. */
export function CardLabel({ children }: { children: ReactNode }) {
  return (
    <p style={{
      margin:        0,
      fontFamily:    font.sans,
      fontSize:      fontSize.xs,
      fontWeight:    fontWeight.semibold,
      color:         fg.secondary,
      textTransform: "uppercase",
      letterSpacing: "0.05em",
    }}>
      {children}
    </p>
  );
}
