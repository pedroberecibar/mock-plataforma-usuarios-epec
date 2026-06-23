import type { ReactNode } from "react";
import { fg, font, fontSize, fontWeight, space } from "../design-tokens";

interface Props {
  children: ReactNode;
  marginBottom?: number;
}

export function SectionTitle({ children, marginBottom = space[4] }: Props) {
  return (
    <h3
      style={{
        fontFamily:   font.sans,
        fontSize:     fontSize.md,
        fontWeight:   fontWeight.semibold,
        color:        fg.primary,
        margin:       0,
        marginBottom,
        lineHeight:   1.3,
      }}
    >
      {children}
    </h3>
  );
}
