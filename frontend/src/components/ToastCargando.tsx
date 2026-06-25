import { bg, border, fg, font, fontSize, radius, space } from "../design-tokens";

function SpinnerIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={{
        flexShrink: 0,
        animation: "spin 1.2s linear infinite",
      }}
    >
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </svg>
  );
}

export function ToastCargando() {
  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        background:   bg.surfaceFeat,
        border:       `1px solid ${border.default}`,
        borderRadius: `${radius.lg}px`,
        boxShadow:    "0 2px 8px rgba(100,80,60,0.08)",
        padding:      `${space[3]}px ${space[5]}px`,
        display:      "flex",
        alignItems:   "center",
        gap:          space[3],
        marginBottom: space[6],
        fontFamily:   font.sans,
        color:        fg.secondary,
      }}
    >
      <SpinnerIcon />
      <span style={{ fontSize: fontSize.sm }}>
        Estamos terminando de cargar tu información, esto puede tardar unos segundos…
      </span>
    </div>
  );
}
