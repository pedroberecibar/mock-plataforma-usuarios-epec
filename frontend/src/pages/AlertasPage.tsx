import { useEffect, useState } from "react";
import type React from "react";
import { fetchAlertasConfig, patchAlertaConfig } from "../api/alertas";
import {
  bg, border, brand, color, fg,
  font, fontSize, fontWeight, radius, space,
  cardStyle,
} from "../design-tokens";

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

  return (
    <div style={{ padding: space[6], fontFamily: font.sans, maxWidth: 680, margin: "0 auto" }}>

      <h2 style={pageTitleStyle}>Configuración de notificaciones</h2>
      <p style={{ ...captionStyle, marginBottom: space[6] }}>
        Elegí qué avisos querés recibir por correo electrónico.
      </p>

      {error && (
        <p role="alert" style={errorStyle}>{error}</p>
      )}

      {loading ? (
        <p style={captionStyle}>Cargando configuración…</p>
      ) : (
        <div style={{ ...cardStyle, padding: 0, overflow: "hidden" }}>
          {/* Section header */}
          <div style={sectionHeaderStyle}>
            <IconMail />
            <span style={{ fontWeight: fontWeight.semibold, fontSize: fontSize.sm, color: fg.primary }}>
              Alertas por email
            </span>
          </div>

          {/* Toggle items */}
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
        </div>
      )}

      {/* Info notice */}
      <div style={infoNoticeStyle}>
        <IconInfo />
        <span style={{ fontSize: fontSize.sm, color: fg.secondary, lineHeight: 1.5 }}>
          Los avisos se envían al correo electrónico asociado a tu cuenta. Podés cambiar
          esta configuración en cualquier momento.
        </span>
      </div>
    </div>
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
        display:      "flex",
        alignItems:   "center",
        justifyContent: "space-between",
        padding:      `${space[4]}px ${space[5]}px`,
        borderBottom: isLast ? "none" : `1px solid ${border.default}`,
        gap:          space[4],
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
// Styles
// ---------------------------------------------------------------------------
const pageTitleStyle: React.CSSProperties = {
  fontFamily:   font.sans,
  fontSize:     fontSize.xl,
  fontWeight:   fontWeight.semibold,
  color:        fg.primary,
  margin:       0,
  marginBottom: space[2],
};

const captionStyle: React.CSSProperties = {
  fontFamily: font.sans,
  fontSize:   fontSize.sm,
  color:      fg.secondary,
  margin:     0,
  lineHeight: 1.5,
};

const sectionHeaderStyle: React.CSSProperties = {
  display:       "flex",
  alignItems:    "center",
  gap:           space[2],
  padding:       `${space[3]}px ${space[5]}px`,
  background:    bg.muted,
  borderBottom:  `1px solid ${border.default}`,
};

const infoNoticeStyle: React.CSSProperties = {
  display:       "flex",
  alignItems:    "flex-start",
  gap:           space[2],
  marginTop:     space[5],
  padding:       `${space[3]}px ${space[4]}px`,
  background:    bg.muted,
  borderRadius:  radius.md,
  border:        `1px solid ${border.default}`,
};

const errorStyle: React.CSSProperties = {
  fontFamily:    font.sans,
  fontSize:      fontSize.sm,
  color:         color.error,
  background:    color.errorLight,
  border:        `1px solid ${color.error}`,
  borderRadius:  radius.sm,
  padding:       `${space[2]}px ${space[3]}px`,
  margin:        0,
  marginBottom:  space[4],
};
