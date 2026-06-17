/**
 * EPEC Design System — Design Tokens
 * Empresa Provincial de Energía de Córdoba
 *
 * Source of truth: docs/EPEC Design System/colors_and_type.css
 * These constants mirror the CSS custom properties for use in React inline styles.
 */

// ---------------------------------------------------------------------------
// COLOR PALETTE — Primary green scale
// ---------------------------------------------------------------------------
export const color = {
  green900: "#0a2e1b",
  green800: "#0f3d24",
  green700: "#124e2f", // BRAND PRIMARY
  green600: "#1a6640",
  green500: "#227d50",
  green400: "#3a9e6e",
  green300: "#6dbf97",
  green200: "#a8d9c0",
  green100: "#d4eedd",
  green50:  "#edf5f0",

  // Neutral scale
  neutral900: "#111614",
  neutral800: "#1e2421",
  neutral700: "#2f3733",
  neutral600: "#4a5550",
  neutral500: "#6b7772",
  neutral400: "#8f9c97",
  neutral300: "#b5bfbb",
  neutral200: "#d5ddd9",
  neutral100: "#eaeeec",
  neutral50:  "#f5f7f6",
  white:      "#ffffff",

  // Semantic status
  successDark:   "#155a2e",
  success:       "#1d8348",
  successLight:  "#d4edda",
  warningDark:   "#7a4a00",
  warning:       "#e6910a",
  warningLight:  "#fff3cd",
  errorDark:     "#7a1c1c",
  error:         "#c0392b",
  errorLight:    "#fde8e8",
  infoDark:      "#0d4272",
  info:          "#1565c0",
  infoLight:     "#dbeafe",
} as const;

// ---------------------------------------------------------------------------
// SEMANTIC UI TOKENS
// ---------------------------------------------------------------------------
export const bg = {
  page:     color.neutral50,
  surface:  color.white,
  sidebar:  color.green700,
  header:   color.green700,
  hover:    color.green50,
  selected: color.green100,
  muted:    color.neutral100,
} as const;

export const fg = {
  primary:   color.neutral900,
  secondary: color.neutral600,
  muted:     color.neutral400,
  onDark:    color.white,
  link:      color.green600,
  linkHover: color.green700,
} as const;

export const border = {
  default: color.neutral200,
  strong:  color.neutral300,
  focus:   color.green500,
  brand:   color.green700,
} as const;

export const brand = {
  primary: color.green700,
  hover:   color.green600,
  pressed: color.green800,
} as const;

// ---------------------------------------------------------------------------
// TYPOGRAPHY
// ---------------------------------------------------------------------------
export const font = {
  sans:      "'Roboto', 'Segoe UI', sans-serif",
  technical: "'Space Grotesk', 'Segoe UI', sans-serif",
} as const;

export const fontSize = {
  xs:   11,
  sm:   13,
  base: 15,
  md:   17,
  lg:   20,
  xl:   24,
  "2xl": 28,
  "3xl": 34,
  "4xl": 42,
} as const;

export const fontWeight = {
  regular:  400,
  medium:   500,
  semibold: 600,
  bold:     700,
} as const;

export const lineHeight = {
  tight:   1.2,
  snug:    1.35,
  normal:  1.5,
  relaxed: 1.65,
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
// BORDER RADIUS
// ---------------------------------------------------------------------------
export const radius = {
  xs:   2,
  sm:   4,
  md:   6,
  lg:   8,
  xl:   12,
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
  border:       `1px solid ${border.default}`,
  borderRadius: radius.sm,
  boxShadow:    shadow.sm,
  padding:      space[6],
  fontFamily:   font.sans,
};

export const labelStyle: React.CSSProperties = {
  fontFamily:  font.sans,
  fontSize:    fontSize.sm,
  fontWeight:  fontWeight.medium,
  color:       fg.secondary,
  margin:      0,
  marginBottom: space[1],
  lineHeight:  lineHeight.normal,
};

export const captionStyle: React.CSSProperties = {
  fontFamily: font.sans,
  fontSize:   fontSize.xs,
  color:      fg.muted,
  margin:     0,
  lineHeight: lineHeight.normal,
};

// Re-export React type so importing files don't need to import React separately
import type React from "react";
