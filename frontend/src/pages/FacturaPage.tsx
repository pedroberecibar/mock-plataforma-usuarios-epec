import { useState } from "react";
import { fetchLinkFactura } from "../api/factura";
import {
  bg, border, brand, color, fg,
  font, fontSize, fontWeight, radius, space,
  cardStyle, labelStyle,
} from "../design-tokens";

interface Props {
  token: string;
}

interface Concepto {
  titulo: string;
  descripcion: string;
}

const CONCEPTOS: Concepto[] = [
  {
    titulo: "Energía",
    descripcion:
      "El costo del kWh que consumís, calculado según la tarifa T1 residencial vigente en EPEC.",
  },
  {
    titulo: "Transporte",
    descripcion:
      "Cargo por el uso de las líneas de alta tensión que transportan la energía desde las centrales.",
  },
  {
    titulo: "Distribución (VAD)",
    descripcion:
      "Valor Agregado de Distribución: cubre la red de media y baja tensión que lleva la energía hasta tu domicilio.",
  },
  {
    titulo: "Cargo fijo",
    descripcion:
      "Costo mensual fijo por tener el suministro habilitado, independientemente del consumo.",
  },
  {
    titulo: "Impuestos",
    descripcion:
      "IVA, impuesto provincial y otros cargos determinados por ley, aplicados sobre el total.",
  },
];

export function FacturaPage({ token }: Props) {
  const [numeroCliente, setNumeroCliente] = useState("");
  const [numeroContrato, setNumeroContrato] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandido, setExpandido] = useState<number | null>(null);

  async function handleIrAFactura(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const url = await fetchLinkFactura(token, numeroCliente, numeroContrato);
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (err) {
      if (err instanceof Error && err.message === "no_configurado") {
        setError("El acceso a la factura EPEC aún no está configurado. Ingresá directamente en epec.com.ar.");
      } else {
        setError("No se pudo generar el enlace. Intentá de nuevo.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: space[6], fontFamily: font.sans, maxWidth: 700, margin: "0 auto" }}>

      {/* Conceptos */}
      <section style={{ marginBottom: space[8] }}>
        <h2 style={sectionTitleStyle}>Conceptos de tu factura</h2>
        <p style={{ ...captionStyle, marginBottom: space[4] }}>
          Tu factura EPEC se mide en kWh. Estos son los conceptos que la componen:
        </p>
        <div style={{ display: "flex", flexDirection: "column", gap: space[2] }}>
          {CONCEPTOS.map((c, i) => (
            <div key={c.titulo} style={{ ...cardStyle, padding: `${space[3]}px ${space[4]}px` }}>
              <button
                onClick={() => setExpandido(expandido === i ? null : i)}
                aria-expanded={expandido === i}
                style={{
                  display:        "flex",
                  alignItems:     "center",
                  justifyContent: "space-between",
                  width:          "100%",
                  background:     "none",
                  border:         "none",
                  cursor:         "pointer",
                  padding:        0,
                  fontFamily:     font.sans,
                  fontSize:       fontSize.base,
                  fontWeight:     fontWeight.medium,
                  color:          fg.primary,
                  textAlign:      "left",
                }}
              >
                {c.titulo}
                <ChevronIcon open={expandido === i} />
              </button>
              {expandido === i && (
                <p style={{ ...captionStyle, marginTop: space[2], marginBottom: 0 }}>
                  {c.descripcion}
                </p>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Link a factura EPEC */}
      <section>
        <h2 style={sectionTitleStyle}>Ver, descargar y pagar tu factura</h2>
        <div style={{ ...cardStyle, padding: space[6] }}>
          <p style={{ ...captionStyle, marginBottom: space[5] }}>
            Ingresá tu Nº de cliente y Nº de contrato para ir directamente a tu factura en el sitio de EPEC.
          </p>
          <form onSubmit={handleIrAFactura} noValidate>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: space[4], marginBottom: space[5] }}>
              <div>
                <label htmlFor="numero-cliente" style={labelStyle}>Nº de cliente</label>
                <input
                  id="numero-cliente"
                  type="text"
                  value={numeroCliente}
                  onChange={(e) => setNumeroCliente(e.target.value)}
                  placeholder="Ej: 123456"
                  required
                  disabled={loading}
                  style={inputStyle}
                />
              </div>
              <div>
                <label htmlFor="numero-contrato" style={labelStyle}>Nº de contrato</label>
                <input
                  id="numero-contrato"
                  type="text"
                  value={numeroContrato}
                  onChange={(e) => setNumeroContrato(e.target.value)}
                  placeholder="Ej: 789012"
                  required
                  disabled={loading}
                  style={inputStyle}
                />
              </div>
            </div>

            {error && (
              <p role="alert" style={errorStyle}>{error}</p>
            )}

            <button
              type="submit"
              disabled={loading || !numeroCliente || !numeroContrato}
              style={{
                display:      "inline-flex",
                alignItems:   "center",
                gap:          space[2],
                background:   brand.primary,
                color:        color.white,
                border:       "none",
                borderRadius: radius.md,
                padding:      `${space[3]}px ${space[5]}px`,
                fontSize:     fontSize.base,
                fontWeight:   fontWeight.semibold,
                fontFamily:   font.sans,
                cursor:       loading || !numeroCliente || !numeroContrato ? "not-allowed" : "pointer",
                opacity:      loading || !numeroCliente || !numeroContrato ? 0.6 : 1,
              }}
            >
              <IconExternalLink />
              {loading ? "Abriendo…" : "Ir a mi factura"}
            </button>
          </form>

          <p style={{ ...captionStyle, marginTop: space[4], color: fg.muted }}>
            Te avisaremos por notificación cuando tu próxima factura esté disponible.
          </p>
        </div>
      </section>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------
function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
      style={{ flexShrink: 0, transform: open ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.15s" }}
      aria-hidden="true"
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

function IconExternalLink() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
const sectionTitleStyle: React.CSSProperties = {
  fontFamily:   font.sans,
  fontSize:     fontSize.lg,
  fontWeight:   fontWeight.semibold,
  color:        fg.primary,
  margin:       0,
  marginBottom: space[3],
};

const captionStyle: React.CSSProperties = {
  fontFamily:  font.sans,
  fontSize:    fontSize.sm,
  color:       fg.secondary,
  margin:      0,
  lineHeight:  1.5,
};

const inputStyle: React.CSSProperties = {
  display:      "block",
  width:        "100%",
  boxSizing:    "border-box",
  fontFamily:   font.sans,
  fontSize:     fontSize.base,
  color:        fg.primary,
  background:   bg.surface,
  border:       `1px solid ${border.default}`,
  borderRadius: radius.md,
  padding:      `${space[3]}px ${space[4]}px`,
  outline:      "none",
};

const errorStyle: React.CSSProperties = {
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

import type React from "react";
