import type { ReactNode } from "react";
import { color, font, fontSize, radius, space } from "../design-tokens";


type Variant = "success" | "warning" | "error" | "info";

interface Props {
  variant: Variant;
  children: ReactNode;
  "data-testid"?: string;
}

const BORDER_COLOR: Record<Variant, string> = {
  success: color.green500,
  warning: "#e6910a",
  error:   color.error,
  info:    "#1565c0",
};

const BG_COLOR: Record<Variant, string> = {
  success: "rgba(18,78,47,0.06)",
  warning: "rgba(230,145,10,0.08)",
  error:   "rgba(192,57,43,0.06)",
  info:    "rgba(21,101,192,0.06)",
};

const TEXT_COLOR: Record<Variant, string> = {
  success: "#155a2e",
  warning: "#7a4a00",
  error:   color.errorDark,
  info:    "#0d4272",
};

export function AlertBanner({ variant, children, "data-testid": testId }: Props) {
  return (
    <div
      role="alert"
      data-testid={testId}
      style={{
        display:      "flex",
        alignItems:   "flex-start",
        gap:          space[3],
        padding:      `${space[3]}px ${space[4]}px`,
        background:   BG_COLOR[variant],
        borderLeft:   `3px solid ${BORDER_COLOR[variant]}`,
        borderRadius: `0 ${radius.md}px ${radius.md}px 0`,
        fontFamily:   font.sans,
        fontSize:     fontSize.sm,
        color:        TEXT_COLOR[variant],
        lineHeight:   1.5,
      }}
    >
      {children}
    </div>
  );
}
