import type { ReactNode } from "react";
import {
  bg, border, fg, font, fontSize, fontWeight, space,
} from "../design-tokens";

interface Props {
  title: string;
  actions?: ReactNode;
}

export function PageHeader({ title, actions }: Props) {
  return (
    <header
      role="banner"
      style={{
        height:         64,
        display:        "flex",
        alignItems:     "center",
        justifyContent: "space-between",
        padding:        `0 ${space[10]}px`,
        background:     bg.page,
        borderBottom:   `1px solid ${border.default}`,
        position:       "sticky",
        top:            0,
        zIndex:         40,
        flexShrink:     0,
      }}
    >
      <h2
        style={{
          fontFamily:    font.sans,
          fontSize:      fontSize["2xl"],
          fontWeight:    fontWeight.semibold,
          color:         fg.link,
          margin:        0,
          letterSpacing: "-0.01em",
          lineHeight:    1.25,
        }}
      >
        {title}
      </h2>
      {actions && (
        <div style={{ display: "flex", alignItems: "center", gap: space[3] }}>
          {actions}
        </div>
      )}
    </header>
  );
}
