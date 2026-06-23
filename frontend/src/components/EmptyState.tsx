import { bg, color, fg, font, fontSize, fontWeight, radius, space } from "../design-tokens";

interface Props {
  title: string;
  description?: string;
  ctaLabel?: string;
  onCta?: () => void;
}

export function EmptyState({ title, description, ctaLabel, onCta }: Props) {
  return (
    <div
      role="status"
      style={{
        display:        "flex",
        flexDirection:  "column",
        alignItems:     "center",
        justifyContent: "center",
        textAlign:      "center",
        padding:        `${space[12]}px ${space[8]}px`,
        background:     bg.surfaceFeat,
        borderRadius:   radius.lg,
        gap:            space[3],
      }}
    >
      <svg
        width="40" height="40" viewBox="0 0 24 24" fill="none"
        stroke={color.green300} strokeWidth="1.5"
        strokeLinecap="round" strokeLinejoin="round"
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <p style={{
        fontFamily: font.sans,
        fontSize:   fontSize.base,
        fontWeight: fontWeight.semibold,
        color:      fg.primary,
        margin:     0,
      }}>
        {title}
      </p>
      {description && (
        <p style={{
          fontFamily: font.sans,
          fontSize:   fontSize.sm,
          color:      fg.muted,
          margin:     0,
          maxWidth:   320,
          lineHeight: 1.5,
        }}>
          {description}
        </p>
      )}
      {ctaLabel && onCta && (
        <button
          onClick={onCta}
          style={{
            marginTop:    space[2],
            padding:      `${space[3]}px ${space[5]}px`,
            background:   color.green700,
            color:        "#ffffff",
            border:       "none",
            borderRadius: radius.md,
            fontSize:     fontSize.sm,
            fontWeight:   fontWeight.semibold,
            fontFamily:   font.sans,
            cursor:       "pointer",
          }}
        >
          {ctaLabel}
        </button>
      )}
    </div>
  );
}
