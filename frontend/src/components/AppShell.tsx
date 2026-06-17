import type React from "react";
import { useEffect, useState } from "react";
import { color, font, fontSize, fontWeight, space } from "../design-tokens";

function useIsMobile(breakpoint = 768): boolean {
  const [isMobile, setIsMobile] = useState(() => window.innerWidth < breakpoint);
  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth < breakpoint);
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, [breakpoint]);
  return isMobile;
}

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

const IconSettings = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export type Vista = "home" | "consumo";

interface NavItem {
  label: string;
  vista: Vista | null;
  icon: React.ReactNode;
  disabled: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Inicio",        vista: "home",         icon: <IconHome />,     disabled: false },
  { label: "Consumo",       vista: "consumo",      icon: <IconBarChart />, disabled: false },
  { label: "Objetivos",     vista: null,           icon: <IconTarget />,   disabled: true },
  { label: "Mi factura",    vista: null,           icon: <IconReceipt />,  disabled: true },
  { label: "Configuración", vista: null,           icon: <IconSettings />, disabled: true },
];

interface AppShellProps {
  vistaActiva: Vista;
  onNavegar: (vista: Vista) => void;
  usuarioNombre?: string;
  children: React.ReactNode;
}

// ---------------------------------------------------------------------------
// Color constants used in this component
// ---------------------------------------------------------------------------
const C = {
  bg:           color.green700,
  activeItem:   color.green600,
  hoverItem:    color.green800,
  textActive:   color.white,
  textEnabled:  color.green200,
  textDisabled: color.green300,
  content:      color.neutral50,
} as const;

// ---------------------------------------------------------------------------
// AppShell component
// ---------------------------------------------------------------------------
export function AppShell({ vistaActiva, onNavegar, usuarioNombre, children }: AppShellProps) {
  const isMobile = useIsMobile();

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", fontFamily: font.sans }}>
      {/* Header */}
      <header
        style={{
          background:     C.bg,
          height:         56,
          display:        "flex",
          alignItems:     "center",
          padding:        `0 ${space[6]}px`,
          flexShrink:     0,
          justifyContent: "space-between",
          zIndex:         10,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: space[3] }}>
          <img src="/epec-logo-white.png" alt="EPEC" height={32} />
          <span
            style={{
              color:      color.green200,
              fontSize:   fontSize.xs,
              fontWeight: fontWeight.medium,
              letterSpacing: "0.03em",
            }}
          >
            Plataforma de Clientes
          </span>
        </div>
        <span
          style={{
            color:      color.white,
            fontSize:   fontSize.sm,
            fontWeight: fontWeight.regular,
          }}
        >
          {usuarioNombre ?? "Mi cuenta"}
        </span>
      </header>

      {/* Body: sidebar + content (desktop) / content + bottom-nav (mobile) */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Desktop sidebar — hidden on mobile */}
        {!isMobile && (
          <nav
            aria-label="Navegación principal"
            style={{
              width:         220,
              background:    C.bg,
              display:       "flex",
              flexDirection: "column",
              padding:       `${space[4]}px 0`,
              flexShrink:    0,
            }}
          >
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.label}
                item={item}
                isActive={item.vista === vistaActiva}
                onNavegar={onNavegar}
              />
            ))}
          </nav>
        )}

        {/* Main content */}
        <main
          style={{
            flex:       1,
            background: C.content,
            overflowY:  "auto",
          }}
        >
          {children}
        </main>
      </div>

      {/* Mobile bottom navigation — hidden on desktop */}
      {isMobile && (
        <nav
          aria-label="Navegación inferior"
          style={{
            background:     C.bg,
            height:         60,
            display:        "flex",
            alignItems:     "center",
            justifyContent: "space-around",
            flexShrink:     0,
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
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// NavLink — sidebar item
// ---------------------------------------------------------------------------
interface NavLinkProps {
  item: NavItem;
  isActive: boolean;
  onNavegar: (vista: Vista) => void;
}

function NavLink({ item, isActive, onNavegar }: NavLinkProps) {
  const textColor = item.disabled
    ? C.textDisabled
    : isActive
      ? C.textActive
      : C.textEnabled;

  const bg = isActive ? C.activeItem : "transparent";

  function handleClick(e: React.MouseEvent) {
    e.preventDefault();
    if (!item.disabled && item.vista) {
      onNavegar(item.vista);
    }
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
        padding:        `${space[3]}px ${space[5]}px`,
        color:          textColor,
        background:     bg,
        fontWeight:     isActive ? fontWeight.semibold : fontWeight.regular,
        fontSize:       fontSize.sm,
        textDecoration: "none",
        cursor:         item.disabled ? "not-allowed" : "pointer",
        pointerEvents:  item.disabled ? "none" : "auto",
        transition:     "background 0.15s",
        userSelect:     "none",
      }}
    >
      {item.icon}
      {item.label}
    </a>
  );
}

// ---------------------------------------------------------------------------
// BottomNavItem — mobile bottom bar item
// ---------------------------------------------------------------------------
interface BottomNavItemProps {
  item: NavItem;
  isActive: boolean;
  onNavegar: (vista: Vista) => void;
}

function BottomNavItem({ item, isActive, onNavegar }: BottomNavItemProps) {
  const textColor = item.disabled
    ? C.textDisabled
    : isActive
      ? C.textActive
      : C.textEnabled;

  function handleClick(e: React.MouseEvent) {
    e.preventDefault();
    if (!item.disabled && item.vista) {
      onNavegar(item.vista);
    }
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
        fontSize:       10,
        textDecoration: "none",
        cursor:         item.disabled ? "not-allowed" : "pointer",
        pointerEvents:  item.disabled ? "none" : "auto",
        userSelect:     "none",
        padding:        `${space[2]}px ${space[3]}px`,
      }}
    >
      {item.icon}
      {item.label}
    </a>
  );
}
