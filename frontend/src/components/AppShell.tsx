import type React from "react";
import { bg, color, font, fontSize, fontWeight, space, radius, brand } from "../design-tokens";

// ---------------------------------------------------------------------------
// Vista → página title mapping (used by mobile top bar)
// ---------------------------------------------------------------------------
export type Vista = "home" | "consumo" | "objetivos" | "factura" | "alertas" | "cuenta";

const VISTA_LABELS: Record<Vista, string> = {
  home:      "Inicio",
  consumo:   "Mi Consumo",
  objetivos: "Objetivos",
  factura:   "Mi Factura",
  alertas:   "Alertas",
  cuenta:    "Mi cuenta",
};

// ---------------------------------------------------------------------------
// SVG icons — inline, no external dependency
// ---------------------------------------------------------------------------
const IconHome = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
);

const IconBarChart = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <line x1="18" y1="20" x2="18" y2="10" />
    <line x1="12" y1="20" x2="12" y2="4" />
    <line x1="6" y1="20" x2="6" y2="14" />
  </svg>
);

const IconTarget = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="6" />
    <circle cx="12" cy="12" r="2" />
  </svg>
);

const IconReceipt = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <polyline points="6 9 6 2 18 2 18 9" />
    <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
    <rect x="6" y="14" width="12" height="8" />
  </svg>
);

const IconBell = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
  </svg>
);

const IconLogout = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <polyline points="16 17 21 12 16 7" />
    <line x1="21" y1="12" x2="9" y2="12" />
  </svg>
);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface NavItem {
  label: string;
  vista: Vista | null;
  icon: React.ReactNode;
  disabled: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Inicio",     vista: "home",      icon: <IconHome />,     disabled: false },
  { label: "Consumo",    vista: "consumo",   icon: <IconBarChart />, disabled: false },
  { label: "Objetivos",  vista: "objetivos", icon: <IconTarget />,   disabled: false },
  { label: "Mi factura", vista: "factura",   icon: <IconReceipt />,  disabled: false },
  { label: "Alertas",    vista: "alertas",   icon: <IconBell />,     disabled: false },
];

interface AppShellProps {
  vistaActiva: Vista;
  onNavegar: (vista: Vista) => void;
  onLogout: () => void;
  usuarioNombre?: string;
  children: React.ReactNode;
}

// ---------------------------------------------------------------------------
// Color constants — aligned with Stitch primary-container palette
// ---------------------------------------------------------------------------
const C = {
  bg:                color.green700,
  activeItemBg:      color.green400,
  activeItemOverlay: brand.navActiveOverlay,
  activeItemText:    color.green700,
  textActive:        color.white,
  textEnabled:       color.white,
  textDisabled:      color.green300,
  content:           bg.page,
} as const;

// ---------------------------------------------------------------------------
// AppShell
// ---------------------------------------------------------------------------
export function AppShell({ vistaActiva, onNavegar, onLogout, usuarioNombre, children }: AppShellProps) {
  const initials = usuarioNombre
    ? usuarioNombre.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "EP";

  return (
    <div style={{ display: "flex", fontFamily: font.sans, minHeight: "100vh" }}>

      {/* ── Mobile top bar — CSS shows on mobile, hides on desktop ── */}
      <nav
        className="app-topbar"
        data-testid="mobile-topbar"
        aria-label="Barra superior"
        style={{
          background:     C.bg,
          height:         60,
          alignItems:     "center",
          justifyContent: "space-between",
          padding:        `0 ${space[5]}px`,
          position:       "fixed",
          top:            0,
          left:           0,
          right:          0,
          zIndex:         50,
          flexShrink:     0,
        }}
      >
        <img
          src="/epec-logo-transparent.png"
          alt="EPEC logo"
          style={{ height: 32, width: "auto", objectFit: "contain" }}
        />
        <span style={{
          color:         color.white,
          fontSize:      fontSize.base,
          fontWeight:    fontWeight.semibold,
          fontFamily:    font.sans,
          letterSpacing: "0.01em",
          position:      "absolute",
          left:          "50%",
          transform:     "translateX(-50%)",
        }}>
          {VISTA_LABELS[vistaActiva]}
        </span>
        <div style={{ width: 32 }} />
      </nav>

      {/* ── Desktop sidebar — CSS hides on mobile ── */}
      <nav
        className="app-sidebar"
        aria-label="Navegación principal"
        style={{
          width:         256,
          minWidth:      256,
          background:    C.bg,
          flexDirection: "column",
          flexShrink:    0,
          position:      "fixed",
          top:           0,
          left:          0,
          height:        "100vh",
          zIndex:        50,
          overflowY:     "auto",
          paddingTop:    space[6],
          paddingBottom: space[6],
        }}
      >
        {/* Brand header */}
        <div style={{
          display:      "flex",
          flexDirection: "column",
          alignItems:   "flex-start",
          gap:          space[2],
          padding:      `0 ${space[6]}px`,
          marginBottom: space[10],
        }}>
          <img
            src="/epec-logo-transparent.png"
            alt="EPEC"
            style={{ height: 34, width: "auto", objectFit: "contain" }}
          />
          <p style={{ color: color.white, fontSize: fontSize.xs, fontFamily: font.mono, letterSpacing: "0.05em", margin: 0, opacity: 0.65 }}>
            Portal de Clientes
          </p>
        </div>

        {/* Nav links */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 2 }}>
          {NAV_ITEMS.map((item) => (
            <SidebarItem
              key={item.label}
              item={item}
              isActive={item.vista === vistaActiva}
              onNavegar={onNavegar}
            />
          ))}
        </div>

        {/* User chip + logout at bottom */}
        <div style={{ padding: `0 ${space[6]}px`, marginTop: space[8], display: "flex", flexDirection: "column", gap: space[2] }}>
          <button
            type="button"
            onClick={() => onNavegar("cuenta")}
            aria-current={vistaActiva === "cuenta" ? "page" : undefined}
            aria-label="Ver Mi cuenta"
            style={{
            display:      "flex",
            alignItems:   "center",
            gap:          space[3],
            width:        "100%",
            textAlign:    "left",
            cursor:       "pointer",
            padding:      space[2],
            background:   vistaActiva === "cuenta" ? "rgba(255,255,255,0.20)" : "rgba(255,255,255,0.10)",
            borderRadius: radius.md,
            border:       vistaActiva === "cuenta"
              ? "1px solid rgba(255,255,255,0.30)"
              : "1px solid rgba(255,255,255,0.10)",
            transition:   "background 150ms ease, border 150ms ease",
          }}>
            <div style={{
              width:          40,
              height:         40,
              borderRadius:   radius.full,
              background:     color.secondaryContainer,
              color:          color.onSecondaryContainer,
              display:        "flex",
              alignItems:     "center",
              justifyContent: "center",
              fontWeight:     fontWeight.bold,
              fontSize:       fontSize.sm,
              flexShrink:     0,
            }}>
              {initials}
            </div>
            <div style={{ overflow: "hidden", flex: 1 }}>
              <p style={{
                color:         color.white,
                fontSize:      fontSize.xs,
                fontFamily:    font.mono,
                fontWeight:    fontWeight.bold,
                letterSpacing: "0.05em",
                margin:        0,
                overflow:      "hidden",
                textOverflow:  "ellipsis",
                whiteSpace:    "nowrap",
              }}>
                {usuarioNombre ?? "Mi cuenta"}
              </p>
              <p style={{
                color:      color.green300,
                fontSize:   10,
                fontFamily: font.sans,
                margin:     "2px 0 0",
              }}>
                Ver mis datos
              </p>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={color.green300}
              strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
              style={{ flexShrink: 0 }}>
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>

          <button
            onClick={onLogout}
            aria-label="Cerrar sesión"
            style={{
              display:        "flex",
              alignItems:     "center",
              justifyContent: "center",
              gap:            space[2],
              width:          "100%",
              padding:        `${space[2]}px ${space[3]}px`,
              background:     "rgba(255,255,255,0.08)",
              border:         "1px solid rgba(255,255,255,0.12)",
              borderRadius:   radius.md,
              color:          color.white,
              fontSize:       fontSize.xs,
              fontFamily:     font.sans,
              fontWeight:     fontWeight.medium,
              cursor:         "pointer",
              opacity:        0.8,
            }}
          >
            <IconLogout />
            Cerrar sesión
          </button>
        </div>
      </nav>

      {/* ── Main content — CSS controls margin based on viewport ── */}
      <div className="app-content" style={{ flex: 1, background: C.content, minHeight: "100vh" }}>
        {children}
      </div>

      {/* ── Mobile bottom nav — CSS hides on desktop ── */}
      <nav
        className="app-bottomnav"
        aria-label="Navegación inferior"
        style={{
          background:     C.bg,
          height:         60,
          minHeight:      60,
          alignItems:     "center",
          justifyContent: "space-around",
          flexShrink:     0,
          position:       "fixed",
          bottom:         0,
          left:           0,
          right:          0,
          zIndex:         50,
        }}
      >
        {NAV_ITEMS.map((item) => (
          <BottomNavItem
            key={item.label}
            item={item}
            isActive={item.vista === vistaActiva}
            onNavegar={onNavegar}
          />
        ))}
      </nav>

    </div>
  );
}

// ---------------------------------------------------------------------------
// SidebarItem
// ---------------------------------------------------------------------------
interface SidebarItemProps {
  item: NavItem;
  isActive: boolean;
  onNavegar: (vista: Vista) => void;
}

function SidebarItem({ item, isActive, onNavegar }: SidebarItemProps) {
  const textColor = item.disabled
    ? C.textDisabled
    : isActive
      ? C.activeItemText
      : C.textEnabled;

  const background = item.disabled
    ? "transparent"
    : isActive
      ? C.activeItemBg
      : "transparent";

  function handleClick(e: React.MouseEvent) {
    e.preventDefault();
    if (!item.disabled && item.vista) onNavegar(item.vista);
  }

  return (
    <a
      href={item.disabled ? undefined : "#"}
      role="link"
      aria-current={isActive ? "page" : undefined}
      aria-disabled={item.disabled || undefined}
      onClick={handleClick}
      style={{
        display:        "flex",
        alignItems:     "center",
        gap:            space[3],
        padding:        `${space[3]}px ${space[4]}px`,
        margin:         `0 ${space[2]}px`,
        color:          textColor,
        background,
        borderRadius:   radius.md,
        fontWeight:     isActive ? fontWeight.bold : fontWeight.regular,
        fontSize:       fontSize.base,
        textDecoration: "none",
        cursor:         item.disabled ? "not-allowed" : "pointer",
        pointerEvents:  item.disabled ? "none" : "auto",
        userSelect:     "none",
        opacity:        item.disabled ? 0.5 : !isActive ? 0.8 : 1,
        transition:     "background 150ms ease, opacity 150ms ease",
      }}
    >
      {item.icon}
      {item.label}
    </a>
  );
}

// ---------------------------------------------------------------------------
// BottomNavItem
// ---------------------------------------------------------------------------
interface BottomNavItemProps {
  item: NavItem;
  isActive: boolean;
  onNavegar: (vista: Vista) => void;
}

function BottomNavItem({ item, isActive, onNavegar }: BottomNavItemProps) {
  const textColor = item.disabled ? C.textDisabled : isActive ? C.textActive : C.textEnabled;

  function handleClick(e: React.MouseEvent) {
    e.preventDefault();
    if (!item.disabled && item.vista) onNavegar(item.vista);
  }

  return (
    <a
      href={item.disabled ? undefined : "#"}
      role="link"
      aria-current={isActive ? "page" : undefined}
      aria-disabled={item.disabled || undefined}
      onClick={handleClick}
      style={{
        display:        "flex",
        flexDirection:  "column",
        alignItems:     "center",
        gap:            2,
        color:          textColor,
        opacity:        isActive ? 1 : 0.55,
        fontSize:       10,
        fontWeight:     isActive ? fontWeight.semibold : fontWeight.regular,
        textDecoration: "none",
        cursor:         item.disabled ? "not-allowed" : "pointer",
        pointerEvents:  item.disabled ? "none" : "auto",
        userSelect:     "none",
        padding:        `${space[2]}px ${space[3]}px`,
        transition:     "opacity 150ms ease",
      }}
    >
      {item.icon}
      {item.label}
      {isActive && (
        <div style={{
          width:        4,
          height:       4,
          background:   color.green300,
          borderRadius: radius.full,
          marginTop:    1,
        }} />
      )}
    </a>
  );
}
