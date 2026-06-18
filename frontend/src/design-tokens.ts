/**
 * EPEC Design System — Design Tokens
 * Empresa Provincial de Energía de Córdoba
 *
 * Source of truth: Stitch Desktop project 8454275166029898380
 * Material You color system with EPEC green palette.
 * These constants mirror the Stitch Tailwind config for use in React inline styles.
 */

// ---------------------------------------------------------------------------
// COLOR PALETTE — Material You / EPEC green
// ---------------------------------------------------------------------------
export const color = {
  // Brand green scale (Material You primary role)
  green900: "#002110",  // on-primary-fixed
  green800: "#00361d",  // primary (darkest brand)
  green700: "#124e2f",  // primary-container (sidebar bg)
  green600: "#165131",  // on-primary-fixed-variant
  green500: "#316948",  // surface-tint
  green400: "#84be97",  // on-primary-container (active nav text)
  green300: "#98d4ab",  // primary-fixed-dim / inverse-primary
  green200: "#b4f0c6",  // primary-fixed
  green100: "#d4eedd",  // legacy
  green50:  "#edf5f0",  // legacy

  // Neutral / surface scale (Material You surface roles)
  neutral900: "#191c1d",  // on-surface / on-background
  neutral800: "#2e3132",  // inverse-surface
  neutral700: "#404942",  // on-surface-variant
  neutral600: "#4e6073",  // secondary / on-secondary-container approx
  neutral500: "#717971",  // outline
  neutral400: "#8f9c97",  // legacy
  neutral300: "#c0c9c0",  // outline-variant
  neutral200: "#d9dadb",  // surface-dim
  neutral100: "#e7e8e9",  // surface-container-high
  neutral50:  "#f8f9fa",  // surface / background
  white:      "#ffffff",  // surface-container-lowest

  // Surface containers
  surfaceContainer:        "#edeeef",
  surfaceContainerLow:     "#f3f4f5",
  surfaceContainerHigh:    "#e7e8e9",
  surfaceContainerHighest: "#e1e3e4",

  // Secondary (blue-slate accent)
  secondaryContainer:  "#cfe2f9",
  onSecondaryContainer: "#526478",

  // Tertiary (amber warning)
  tertiaryContainer:    "#6d3500",
  onTertiaryContainer:  "#ff9846",
  tertiaryFixed:        "#ffdcc5",
  onTertiaryFixed:      "#301400",
  onTertiaryFixedVariant: "#713700",

  // Semantic status (Material You error + custom)
  successDark:   "#165131",  // on-primary-fixed-variant (reuse)
  success:       "#316948",  // surface-tint (reuse)
  successLight:  "#b4f0c6",  // primary-fixed
  warningDark:   "#713700",  // on-tertiary-fixed-variant
  warning:       "#ff9846",  // on-tertiary-container
  warningLight:  "#ffdcc5",  // tertiary-fixed
  errorDark:     "#93000a",  // on-error-container
  error:         "#ba1a1a",  // error (Material You)
  errorLight:    "#ffdad6",  // error-container
  infoDark:      "#36485b",  // on-secondary-fixed-variant
  info:          "#4e6073",  // secondary
  infoLight:     "#cfe2f9",  // secondary-container
} as const;

// ---------------------------------------------------------------------------
// SEMANTIC UI TOKENS — mapped to Material You roles
// ---------------------------------------------------------------------------
export const bg = {
  page:     color.neutral50,           // background: #f8f9fa
  surface:  color.white,               // surface-container-lowest: #ffffff
  sidebar:  color.green700,            // primary-container: #124e2f
  header:   color.surfaceContainerLow, // surface-container-low: #f3f4f5 (content header)
  hover:    color.surfaceContainerLow, // surface-container-low
  selected: color.green200,            // primary-fixed: #b4f0c6
  muted:    color.neutral100,          // surface-container-high: #e7e8e9
} as const;

export const fg = {
  primary:   color.neutral900,  // on-surface: #191c1d
  secondary: color.neutral700,  // on-surface-variant: #404942
  muted:     color.neutral500,  // outline: #717971
  onDark:    color.white,       // on-primary: #ffffff
  link:      color.green800,    // primary: #00361d
  linkHover: color.green700,    // primary-container: #124e2f
} as const;

export const border = {
  default: color.neutral300,    // outline-variant: #c0c9c0
  strong:  color.neutral500,    // outline: #717971
  focus:   color.green800,      // primary: #00361d
  brand:   color.green700,      // primary-container: #124e2f
} as const;

export const brand = {
  primary:   color.green700,    // primary-container: #124e2f (used for filled buttons, sidebar)
  hover:     color.green800,    // primary: #00361d (darker on hover)
  pressed:   color.green900,    // on-primary-fixed: #002110
  // Nav item active state (Home screen — pill style)
  navActive:         color.green400,  // on-primary-container: #84be97 (background of active pill)
  navActiveText:     color.green700,  // primary-container: #124e2f (text on active pill)
  // Nav item active state (other screens — semi-transparent overlay)
  navActiveOverlay: "rgba(255,255,255,0.20)",
} as const;

// ---------------------------------------------------------------------------
// TYPOGRAPHY — Stitch font system
// Body/display: Hanken Grotesk. Labels/mono: JetBrains Mono. kWh values: Space Grotesk.
// ---------------------------------------------------------------------------
export const font = {
  sans:      "'Hanken Grotesk', 'Segoe UI', sans-serif",  // body, UI text
  technical: "'Space Grotesk', 'Hanken Grotesk', sans-serif",  // kWh numeric display
  mono:      "'JetBrains Mono', 'Courier New', monospace",  // labels, metadata
} as const;

export const fontSize = {
  xs:    12,  // label-sm: 12px (JetBrains Mono)
  sm:    14,  // small body
  base:  16,  // body-md: 16px
  md:    18,  // body-lg: 18px
  lg:    20,  // title-md: 20px
  xl:    24,  // unit-display: 24px
  "2xl": 32,  // headline-lg: 32px
  "3xl": 40,  // legacy
  "4xl": 48,  // display-lg: 48px
} as const;

export const fontWeight = {
  light:    300,  // unit-display weight
  regular:  400,
  medium:   500,
  semibold: 600,
  bold:     700,
} as const;

export const lineHeight = {
  tight:   1.167,  // 56/48 for display-lg
  snug:    1.25,   // 40/32 for headline-lg
  normal:  1.4,    // 28/20 for title-md
  relaxed: 1.5,    // 24/16 for body-md
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
// BORDER RADIUS — Stitch config: DEFAULT=2px, lg=4px, xl=8px, full=12px
// ---------------------------------------------------------------------------
export const radius = {
  xs:   2,   // DEFAULT in Stitch (0.125rem)
  sm:   4,   // lg in Stitch (0.25rem)
  md:   8,   // xl in Stitch (0.5rem) — cards, inputs, buttons
  lg:   12,  // full in Stitch (0.75rem) — pills, chips
  xl:   16,  // extended for login card
  full: 9999,
} as const;

// ---------------------------------------------------------------------------
// SHADOWS
// ---------------------------------------------------------------------------
export const shadow = {
  xs: "0 1px 2px rgba(0,0,0,0.06)",
  sm: "0 1px 4px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05)",
  md: "0 4px 12px rgba(0,0,0,0.10), 0 1px 3px rgba(0,0,0,0.06)",
  lg: "0 8px 24px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.07)",
  xl: "0 20px 48px rgba(0,0,0,0.15), 0 4px 12px rgba(0,0,0,0.08)",
} as const;

// ---------------------------------------------------------------------------
// COMPOSITE STYLE OBJECTS — shared card container
// ---------------------------------------------------------------------------
export const cardStyle: React.CSSProperties = {
  background:   bg.surface,
  border:       `1px solid ${border.default}`,  // outline-variant #c0c9c0
  borderRadius: radius.md,                       // 8px — rounded-xl in Stitch
  boxShadow:    shadow.sm,
  padding:      space[6],
  fontFamily:   font.sans,
};

export const labelStyle: React.CSSProperties = {
  fontFamily:   font.mono,            // JetBrains Mono for labels (label-sm in Stitch)
  fontSize:     fontSize.xs,          // 12px
  fontWeight:   fontWeight.medium,    // 500
  color:        fg.secondary,         // on-surface-variant #404942
  letterSpacing: "0.05em",            // label-sm tracking in Stitch
  margin:       0,
  marginBottom: space[1],
  lineHeight:   lineHeight.relaxed,
};

export const captionStyle: React.CSSProperties = {
  fontFamily:   font.mono,            // JetBrains Mono
  fontSize:     fontSize.xs,          // 12px
  color:        fg.muted,             // outline #717971
  letterSpacing: "0.05em",
  margin:       0,
  lineHeight:   lineHeight.relaxed,
};

// Re-export React type so importing files don't need to import React separately
import type React from "react";
