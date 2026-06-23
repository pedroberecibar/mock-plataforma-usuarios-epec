import type React from "react";
import { useEffect, useState } from "react";
import { evaluarVencimiento, fetchFacturaDatos } from "../api/factura";
import type { FacturaDatosResponse } from "../api/types";
import {
  bg, brand, fg,
  font, fontSize, fontWeight, radius, space,
  cardStyle,
} from "../design-tokens";
import { PageHeader } from "../components/PageHeader";
import { AlertBanner } from "../components/AlertBanner";
import { SectionTitle } from "../components/SectionTitle";

const EPEC_PAGOS_URL = "https://www.epec.com.ar/tramites/pagos";

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

function diasHastaVencimiento(fechaStr: string): number {
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  const vcto = new Date(fechaStr + "T00:00:00");
  return Math.round((vcto.getTime() - hoy.getTime()) / (1000 * 60 * 60 * 24));
}

function formatFechaVcto(fechaStr: string): string {
  const [y, m, d] = fechaStr.split("-");
  const meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
  return `${parseInt(d)} de ${meses[parseInt(m) - 1]} de ${y}`;
}

export function FacturaPage({ token }: Props) {
  const [expandido, setExpandido] = useState<number | null>(null);
  const [facturaDatos, setFacturaDatos] = useState<FacturaDatosResponse | null>(null);

  useEffect(() => {
    fetchFacturaDatos(token)
      .then(setFacturaDatos)
      .catch(() => { /* fire-and-forget */ });

    evaluarVencimiento(token).catch(() => { /* fire-and-forget */ });
  }, [token]);

  const diasVcto = facturaDatos?.fecha_vencimiento
    ? diasHastaVencimiento(facturaDatos.fecha_vencimiento)
    : null;
  const mostrarBannerVencimiento = diasVcto !== null && diasVcto <= 5;

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <PageHeader title="Mi Factura" />

      <div style={{ maxWidth: 700, margin: "0 auto", padding: `${space[10]}px` }}>

        {mostrarBannerVencimiento && facturaDatos?.fecha_vencimiento && (
          <div style={{ marginBottom: space[5] }}>
            <AlertBanner variant="warning" data-testid="banner-vencimiento">
              ⚠️ Tu factura vence el{" "}
              <strong>{formatFechaVcto(facturaDatos.fecha_vencimiento)}</strong>
              {diasVcto === 0
                ? " — ¡hoy!"
                : diasVcto === 1
                  ? " — ¡mañana!"
                  : ` (en ${diasVcto} días)`}
              . Recordá abonarla para evitar inconvenientes.
            </AlertBanner>
          </div>
        )}

        {facturaDatos?.fecha_vencimiento && !mostrarBannerVencimiento && (
          <p
            data-testid="fecha-vencimiento"
            style={{
              fontFamily:   font.sans,
              fontSize:     fontSize.sm,
              color:        fg.muted,
              marginBottom: space[4],
            }}
          >
            Fecha de vencimiento: {formatFechaVcto(facturaDatos.fecha_vencimiento)}
          </p>
        )}

        <section style={{ marginBottom: space[8] }}>
          <SectionTitle marginBottom={space[3]}>Conceptos de tu factura</SectionTitle>
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

        <section>
          <SectionTitle marginBottom={space[3]}>Ver, descargar y pagar tu factura</SectionTitle>
          <div style={{ ...cardStyle, padding: space[6] }}>
            <p style={{ ...captionStyle, marginBottom: space[5] }}>
              Accedé al portal oficial de EPEC para ver tus facturas, descargarlas y realizar el pago online.
            </p>
            <a
              data-testid="enlace-epec"
              href={EPEC_PAGOS_URL}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display:        "inline-flex",
                alignItems:     "center",
                gap:            space[2],
                background:     brand.primary,
                color:          fg.onDark,
                borderRadius:   radius.md,
                padding:        `${space[3]}px ${space[5]}px`,
                fontSize:       fontSize.base,
                fontWeight:     fontWeight.semibold,
                fontFamily:     font.sans,
                textDecoration: "none",
              }}
            >
              Ver mi factura
            </a>
            <p style={{ ...captionStyle, marginTop: space[4], color: fg.muted }}>
              Te avisaremos por notificación cuando tu próxima factura esté disponible.
            </p>
          </div>
        </section>
      </div>
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

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
const captionStyle: React.CSSProperties = {
  fontFamily: font.sans,
  fontSize:   fontSize.sm,
  color:      fg.secondary,
  margin:     0,
  lineHeight: 1.5,
};
