import { useEffect, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import { fetchAlertasConfig, patchAlertaConfig } from "../api/alertas";
import {
  bg, border, brand, color, fg,
  font, fontSize, fontWeight, radius, shadow, space,
} from "../design-tokens";
import { PageHeader } from "../components/PageHeader";
import { LoadingSkeleton } from "../components/LoadingSkeleton";

interface Props {
  token: string;
}

interface AlertMeta {
  tipo: string;
  label: string;
  descripcion: string;
}

const ALERTA_META: AlertMeta[] = [
  {
    tipo: "factura_disponible",
    label: "Factura disponible",
    descripcion: "Recibí un aviso cuando tu nueva factura EPEC esté lista para ver y pagar.",
  },
  {
    tipo: "vencimiento_proximo",
    label: "Vencimiento próximo",
    descripcion: "Te avisamos cuando quedan pocos días para que venza tu factura.",
  },
  {
    tipo: "consumo_anomalo",
    label: "Consumo inusual",
    descripcion: "Alerta si tu consumo diario supera significativamente el promedio de los últimos meses.",
  },
];

export function AlertasPage({ token }: Props) {
  const [config, setConfig] = useState<Map<string, boolean>>(new Map());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchAlertasConfig(token)
      .then((items) => {
        if (!cancelled) {
          const map = new Map(items.map((i) => [i.tipo, i.habilitado]));
          setConfig(map);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("No se pudo cargar la configuración de alertas.");
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function handleToggle(tipo: string, habilitado: boolean) {
    setSaving(tipo);
    setError(null);
    try {
      await patchAlertaConfig(token, tipo, habilitado);
      setConfig((prev) => new Map(prev).set(tipo, habilitado));
    } catch {
      setError("No se pudo guardar el cambio. Intentá de nuevo.");
    } finally {
      setSaving(null);
    }
  }

  const activas = ALERTA_META.filter((m) => config.get(m.tipo) ?? false).length;

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <PageHeader title="Alertas" />

      <main aria-label="configuración de alertas del cliente">
        <div style={{ maxWidth: 1400, margin: "0 auto", padding: `${space[10]}px` }}>

          {error && (
            <p role="alert" style={errorStyle}>{error}</p>
          )}

          {loading ? (
            <>
              <LoadingSkeleton variant="card" />
              <div style={{ height: space[6] }} />
              <LoadingSkeleton variant="card" />
            </>
          ) : (
            <>
              {/* Row 1 — Hero: resumen de avisos activos a todo el ancho */}
              <HeroAlertas activas={activas} total={ALERTA_META.length} />

              {/* Row 2 — Card de configuración de toggles */}
              <Card style={{ marginBottom: space[4], padding: 0, overflow: "hidden" }}>
                <div style={sectionHeaderStyle}>
                  <IconMail />
                  <span style={{ fontWeight: fontWeight.semibold, fontSize: fontSize.sm, color: fg.primary }}>
                    Alertas por email
                  </span>
                </div>

                <div>
                  {ALERTA_META.map((meta, index) => (
                    <ToggleRow
                      key={meta.tipo}
                      meta={meta}
                      habilitado={config.get(meta.tipo) ?? false}
                      disabled={saving === meta.tipo}
                      isLast={index === ALERTA_META.length - 1}
                      onChange={(v) => handleToggle(meta.tipo, v)}
                    />
                  ))}
                </div>
              </Card>

              {/* Row 3 — Nota informativa */}
              <div style={infoNoticeStyle}>
                <IconInfo />
                <span style={{ fontSize: fontSize.sm, color: fg.secondary, lineHeight: 1.5 }}>
                  Los avisos se envían al correo electrónico asociado a tu cuenta. Podés cambiar
                  esta configuración en cualquier momento.
                </span>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Row 1 — Hero: avisos activos
// ---------------------------------------------------------------------------
function HeroAlertas({ activas, total }: { activas: number; total: number }) {
  return (
    <section
      aria-label="Resumen de alertas"
      style={{
        display:        "flex",
        flexWrap:       "wrap",
        gap:            space[6],
        alignItems:     "center",
        justifyContent: "space-between",
        background:     bg.surfaceFeat,
        borderRadius:   `${radius.lg}px`,
        boxShadow:      shadow.sm,
        padding:        `${space[6]}px`,
        marginBottom:   space[4],
        fontFamily:     font.sans,
      }}
    >
      <div style={{ minWidth: 240 }}>
        <Label>Avisos activos</Label>
        <p style={{
          margin:        `${space[2]}px 0 0`,
          fontFamily:    font.technical,
          fontSize:      fontSize["3xl"],
          fontWeight:    fontWeight.light,
          color:         fg.link,
          lineHeight:    1.1,
          letterSpacing: "-0.02em",
        }}>
          {activas}
          <span style={{ fontFamily: font.sans, fontSize: fontSize.lg, fontWeight: fontWeight.regular, color: fg.secondary, marginLeft: space[2] }}>
            de {total}
          </span>
        </p>
        <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.sm, color: fg.secondary, lineHeight: 1.5 }}>
          Elegí qué avisos querés recibir por correo electrónico.
        </p>
      </div>

      <IconBell />
    </section>
  );
}

// ---------------------------------------------------------------------------
// ToggleRow
// ---------------------------------------------------------------------------
interface ToggleRowProps {
  meta: AlertMeta;
  habilitado: boolean;
  disabled: boolean;
  isLast: boolean;
  onChange: (v: boolean) => void;
}

function ToggleRow({ meta, habilitado, disabled, isLast, onChange }: ToggleRowProps) {
  return (
    <div
      style={{
        display:        "flex",
        alignItems:     "center",
        justifyContent: "space-between",
        padding:        `${space[4]}px ${space[6]}px`,
        borderBottom:   isLast ? "none" : `1px solid ${border.default}`,
        gap:            space[4],
      }}
    >
      <div>
        <p style={{ margin: 0, fontFamily: font.sans, fontSize: fontSize.base, fontWeight: fontWeight.medium, color: fg.primary }}>
          {meta.label}
        </p>
        <p style={{ margin: `${space[1]}px 0 0`, fontFamily: font.sans, fontSize: fontSize.sm, color: fg.secondary, lineHeight: 1.4 }}>
          {meta.descripcion}
        </p>
      </div>
      <Toggle
        checked={habilitado}
        disabled={disabled}
        aria-label={`${habilitado ? "Desactivar" : "Activar"} alerta: ${meta.label}`}
        onChange={onChange}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Toggle switch component
// ---------------------------------------------------------------------------
interface ToggleProps {
  checked: boolean;
  disabled: boolean;
  "aria-label": string;
  onChange: (v: boolean) => void;
}

function Toggle({ checked, disabled, "aria-label": ariaLabel, onChange }: ToggleProps) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      aria-label={ariaLabel}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      style={{
        position:     "relative",
        display:      "inline-flex",
        alignItems:   "center",
        width:        44,
        height:       24,
        borderRadius: 12,
        border:       "none",
        background:   checked ? brand.primary : color.neutral300,
        cursor:       disabled ? "wait" : "pointer",
        opacity:      disabled ? 0.6 : 1,
        flexShrink:   0,
        transition:   "background 0.2s",
        padding:      0,
      }}
    >
      <span
        style={{
          position:     "absolute",
          top:          3,
          left:         checked ? 23 : 3,
          width:        18,
          height:       18,
          borderRadius: "50%",
          background:   color.white,
          boxShadow:    "0 1px 3px rgba(0,0,0,0.2)",
          transition:   "left 0.2s",
        }}
      />
    </button>
  );
}

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------
function IconMail() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ color: brand.primary }}>
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  );
}

function IconBell() {
  return (
    <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ color: brand.primary, opacity: 0.9, flexShrink: 0 }}>
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}

function IconInfo() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ color: fg.muted, flexShrink: 0 }}>
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Primitivos compartidos (mismo lenguaje que Objetivos / Factura / Consumo)
// ---------------------------------------------------------------------------
function Card({ children, style }: { children: ReactNode; style?: CSSProperties }) {
  return (
    <div style={{
      background:   bg.surfaceFeat,
      borderRadius: `${radius.lg}px`,
      boxShadow:    shadow.sm,
      padding:      `${space[6]}px`,
      fontFamily:   font.sans,
      ...style,
    }}>
      {children}
    </div>
  );
}

function Label({ children }: { children: ReactNode }) {
  return (
    <p style={{
      margin:        0,
      fontFamily:    font.sans,
      fontSize:      fontSize.xs,
      fontWeight:    fontWeight.semibold,
      color:         fg.secondary,
      textTransform: "uppercase",
      letterSpacing: "0.05em",
    }}>
      {children}
    </p>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
const sectionHeaderStyle: CSSProperties = {
  display:      "flex",
  alignItems:   "center",
  gap:          space[2],
  padding:      `${space[3]}px ${space[6]}px`,
  background:   bg.muted,
  borderBottom: `1px solid ${border.default}`,
};

const infoNoticeStyle: CSSProperties = {
  display:      "flex",
  alignItems:   "flex-start",
  gap:          space[2],
  padding:      `${space[4]}px ${space[5]}px`,
  background:   bg.surfaceFeat,
  borderRadius: radius.lg,
  boxShadow:    shadow.sm,
};

const errorStyle: CSSProperties = {
  fontFamily:   font.sans,
  fontSize:     fontSize.sm,
  color:        color.error,
  background:   color.errorLight,
  border:       `1px solid ${color.error}`,
  borderRadius: radius.sm,
  padding:      `${space[2]}px ${space[3]}px`,
  margin:       0,
  marginBottom: space[4],
};
