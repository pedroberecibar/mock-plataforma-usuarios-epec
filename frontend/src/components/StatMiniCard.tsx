import { bg, border, fg, font, fontSize, fontWeight, radius, space } from "../design-tokens";

interface Props {
  label: string;
  value: string;
  sub: string;
  accentColor?: string;
  onClick?: () => void;
}

export function StatMiniCard({ label, value, sub, accentColor, onClick }: Props) {
  const isClickable = !!onClick;

  return (
    <div
      onClick={onClick}
      style={{
        background:   bg.surface,
        border:       `1px solid ${border.default}`,
        borderRadius: radius.md,
        padding:      `${space[3]}px ${space[4]}px`,
        cursor:       isClickable ? "pointer" : "default",
        transition:   isClickable ? "box-shadow 150ms ease, transform 150ms ease" : undefined,
      }}
      onMouseEnter={(e) => {
        if (isClickable) {
          (e.currentTarget as HTMLElement).style.boxShadow = "0 4px 12px rgba(100,80,60,0.10)";
          (e.currentTarget as HTMLElement).style.transform = "translateY(-1px)";
        }
      }}
      onMouseLeave={(e) => {
        if (isClickable) {
          (e.currentTarget as HTMLElement).style.boxShadow = "";
          (e.currentTarget as HTMLElement).style.transform = "";
        }
      }}
    >
      <p style={{
        margin:        0,
        fontFamily:    font.sans,
        fontSize:      fontSize.xs,
        fontWeight:    fontWeight.semibold,
        color:         fg.secondary,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
      }}>
        {label}
      </p>
      <p style={{
        margin:     `${space[1]}px 0 ${space[1]}px`,
        fontFamily: font.technical,
        fontSize:   fontSize.md,
        fontWeight: fontWeight.bold,
        color:      accentColor ?? fg.primary,
        lineHeight: 1.2,
      }}>
        {value}
      </p>
      <p style={{
        margin:     0,
        fontFamily: font.sans,
        fontSize:   fontSize.xs,
        color:      fg.muted,
      }}>
        {sub}
      </p>
    </div>
  );
}
