/**
 * EPEC Design System — Design Tokens
 * Empresa Provincial de Energía de Córdoba
 *
 * Source of truth: Stitch Desktop project 8454275166029898380
 * Warm cream surface system inspired by Solora (Phenomenon Studio).
 * These constants mirror the Stitch Tailwind config for use in React inline styles.
 */

// ---------------------------------------------------------------------------
// COLOR PALETTE — Material You / EPEC green (INTOCABLE)
// ---------------------------------------------------------------------------
export const color = {
  // Brand green scale — INTOCABLE
  green900: "#002110",
  green800: "#00361d",
  green700: "#124e2f",
  green600: "#165131",
  green500: "#316948",
  green400: "#84be97",
  green300: "#98d4ab",
  green200: "#b4f0c6",
  green100: "#d4eedd",
  green50:  "#edf5f0",

  // Neutral / surface scale (Material You surface roles)
  neutral900: "#191c1d",
  neutral800: "#2e3132",
  neutral700: "#404942",
  neutral600: "#4e6073",
  neutral500: "#717971",
  neutral400: "#8f9c97",
  neutral300: "#c0c9c0",
  neutral200: "#d9dadb",
  neutral100: "#e7e8e9",
  neutral50:  "#f8f9fa",
  white:      "#ffffff",

  // Surface containers
  surfaceContainer:        "#edeeef",
  surfaceContainerLow:     "#f3f4f5",
  surfaceContainerHigh:    "#e7e8e9",
  surfaceContainerHighest: "#e1e3e4",

  // Secondary (blue-slate accent)
  secondaryContainer:   "#cfe2f9",
  onSecondaryContainer: "#526478",

  // Tertiary (amber warning)
  tertiaryContainer:      "#6d3500",
  onTertiaryContainer:    "#ff9846",
  tertiaryFixed:          "#ffdcc5",
  onTertiaryFixed:        "#301400",
  onTertiaryFixedVariant: "#713700",

  // Semantic status (Material You error + custom)
  successDark:   "#165131",
  success:       "#316948",
  successLight:  "#b4f0c6",
  warningDark:   "#713700",
  warning:       "#ff9846",
  warningLight:  "#ffdcc5",
  errorDark:     "#93000a",
  error:         "#ba1a1a",
  errorLight:    "#ffdad6",
  infoDark:      "#36485b",
  info:          "#4e6073",
  infoLight:     "#cfe2f9",
} as const;

// ---------------------------------------------------------------------------
// SEMANTIC UI TOKENS — Warm cream system
// ---------------------------------------------------------------------------
export const bg = {
  page:        "#F8F6F2",              // warm cream — page background
  surface:     "#FDFCF9",             // warm white — card standard
  surfaceFeat: "#F3EDE2",             // beige visible — card destacada (Solora-style)
  selected:    "#E8DFD0",             // warm selected state
  sidebar:     color.green700,        // #124e2f — intocable
  header:      color.green700,        // #124e2f — intocable
  hover:       "rgba(18,78,47,0.06)", // verde muy sutil en hover
  muted:       "#F3EDE2",             // warm muted bg
} as const;

export const fg = {
  primary:   "#1C1410",        // near-black cálido
  secondary: "#6B5A45",        // warm brown-gray
  muted:     "#8C7A63",        // warm muted
  onDark:    "#ffffff",
  link:      color.green700,   // #124e2f
  linkHover: color.green600,   // #165131
} as const;

export const border = {
  default: "#D4C4A8",       // warm separator — solo cuando necesario
  strong:  "#B0A090",       // warm border fuerte
  focus:   color.green600,  // focus ring
  brand:   color.green700,  // #124e2f
} as const;

export const brand = {
  primary:          color.green700,
  hover:            color.green800,
  pressed:          color.green900,
  navActive:         color.green400,
  navActiveText:     color.green700,
  navActiveOverlay: "rgba(255,255,255,0.20)",
} as const;

// ---------------------------------------------------------------------------
// WARM SURFACE — explicit layer system
// ---------------------------------------------------------------------------
export const warmSurface = {
  0: "#F8F6F2",   // page
  1: "#FDFCF9",   // card standard
  2: "#F3EDE2",   // featured card
  3: "#E8DFD0",   // selected
  4: "#D4C4A8",   // separator
} as const;

// ---------------------------------------------------------------------------
// CHART COLORS
// ---------------------------------------------------------------------------
export const chartColor = {
  primary:       "#1a6640",
  primaryDim:    "rgba(26,102,64,0.30)",
  comparison:    "rgba(180,175,170,0.40)",
  anomaly:       "#c0780a",
  goalLine:      "rgba(18,78,47,0.50)",
  grid:          "rgba(180,170,155,0.30)",
  axisText:      "#8C7A63",
  tooltipBg:     "#F3EDE2",
  tooltipBorder: "#D4C4A8",
} as const;

// ---------------------------------------------------------------------------
// TYPOGRAPHY
// ---------------------------------------------------------------------------
export const font = {
  sans:      "'Inter', 'Segoe UI', system-ui, sans-serif",
  technical: "'Space Grotesk', 'Inter', sans-serif",
  mono:      "'JetBrains Mono', 'Roboto Mono', monospace",
} as const;

export const fontSize = {
  xs:    12,
  sm:    14,
  base:  16,
  md:    18,
  lg:    20,
  xl:    24,
  "2xl": 32,
  "3xl": 40,
  "4xl": 48,
} as const;

export const fontWeight = {
  light:    300,
  regular:  400,
  medium:   500,
  semibold: 600,
  bold:     700,
} as const;

export const lineHeight = {
  tight:   1.167,
  snug:    1.25,
  normal:  1.4,
  relaxed: 1.5,
} as const;

// ---------------------------------------------------------------------------
// SPACING — 4px base grid
// ---------------------------------------------------------------------------
export const space = {
  1:  4,
  2:  8,
  3:  12,
  4:  16,
  5:  20,
  6:  24,
  8:  32,
  10: 40,
  12: 48,
  16: 64,
  20: 80,
} as const;

// ---------------------------------------------------------------------------
// BORDER RADIUS — Solora-inspired generous radii
// ---------------------------------------------------------------------------
export const radius = {
  xs:    4,
  sm:    8,
  md:    12,
  lg:    16,
  xl:    20,
  "2xl": 24,
  full:  9999,
} as const;

// ---------------------------------------------------------------------------
// SHADOWS — warm-tinted (sin negro puro)
// ---------------------------------------------------------------------------
export const shadow = {
  xs:   "0 1px 2px rgba(100,80,60,0.06)",
  sm:   "0 1px 4px rgba(100,80,60,0.08), 0 1px 2px rgba(100,80,60,0.05)",
  md:   "0 4px 12px rgba(100,80,60,0.10), 0 1px 3px rgba(100,80,60,0.06)",
  lg:   "0 8px 24px rgba(100,80,60,0.12), 0 2px 6px rgba(100,80,60,0.07)",
  xl:   "0 20px 48px rgba(100,80,60,0.15), 0 4px 12px rgba(100,80,60,0.08)",
  warm: "0 8px 32px rgba(180,140,80,0.12), 0 2px 8px rgba(100,80,60,0.08)",
} as const;

// ---------------------------------------------------------------------------
// MOTION
// ---------------------------------------------------------------------------
export const motion = {
  duration: { instant: 80, fast: 150, base: 250, slow: 400, xslow: 600 },
  easing: {
    out:    "cubic-bezier(0.0, 0.0, 0.2, 1)",
    inOut:  "cubic-bezier(0.4, 0.0, 0.2, 1)",
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
  },
} as const;

// ---------------------------------------------------------------------------
// COMPOSITE STYLE OBJECTS
// ---------------------------------------------------------------------------
export const cardStyle: React.CSSProperties = {
  background:   bg.surface,
  border:       "none",
  borderRadius: `${radius.lg}px`,
  boxShadow:    shadow.sm,
  padding:      `${space[8]}px`,
  fontFamily:   font.sans,
};

export const cardFeaturedStyle: React.CSSProperties = {
  background:   bg.surfaceFeat,
  border:       "none",
  borderRadius: `${radius.xl}px`,
  boxShadow:    shadow.warm,
  padding:      `${space[10]}px`,
  fontFamily:   font.sans,
};

export const cardAlertStyle = (
  variant: "success" | "warning" | "error" | "info"
): React.CSSProperties => ({
  background:   bg.surface,
  borderLeft:   `3px solid ${
    variant === "success" ? color.green500 :
    variant === "warning" ? "#e6910a" :
    variant === "error"   ? "#c0392b" : "#1565c0"
  }`,
  borderRadius: `0 ${radius.lg}px ${radius.lg}px 0`,
  boxShadow:    shadow.xs,
  padding:      `${space[5]}px ${space[6]}px`,
  fontFamily:   font.sans,
});

export const labelStyle: React.CSSProperties = {
  fontFamily:    font.sans,
  fontSize:      fontSize.xs,
  fontWeight:    fontWeight.medium,
  color:         fg.secondary,
  letterSpacing: "0.05em",
  margin:        0,
  marginBottom:  space[1],
  lineHeight:    lineHeight.relaxed,
};

export const captionStyle: React.CSSProperties = {
  fontFamily:    font.sans,
  fontSize:      fontSize.xs,
  color:         fg.muted,
  letterSpacing: "0.02em",
  margin:        0,
  lineHeight:    lineHeight.relaxed,
};

// Re-export React type so importing files don't need to import React separately
import type React from "react";
