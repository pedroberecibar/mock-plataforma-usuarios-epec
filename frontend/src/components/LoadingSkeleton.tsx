import { bg, radius } from "../design-tokens";

type Variant = "line" | "card" | "chart";

interface Props {
  variant?: Variant;
  count?: number;
  width?: string | number;
}

const HEIGHT: Record<Variant, number> = {
  line:  20,
  card:  120,
  chart: 200,
};

const RADIUS: Record<Variant, number> = {
  line:  radius.sm,
  card:  radius.lg,
  chart: radius.md,
};

export function LoadingSkeleton({ variant = "line", count = 1, width = "100%" }: Props) {
  const height = HEIGHT[variant];
  const borderRadius = RADIUS[variant];

  return (
    <div aria-label="Cargando" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          data-testid="skeleton-block"
          style={{
            width,
            height,
            borderRadius,
            background:  bg.surfaceFeat,
            overflow:    "hidden",
            position:    "relative",
          }}
        >
          <div
            style={{
              position:   "absolute",
              inset:      0,
              background: `linear-gradient(
                90deg,
                transparent 0%,
                rgba(255,255,255,0.55) 50%,
                transparent 100%
              )`,
              animation:  "skeleton-shimmer 1.4s ease-in-out infinite",
            }}
          />
        </div>
      ))}
      <style>{`
        @keyframes skeleton-shimmer {
          0%   { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}
