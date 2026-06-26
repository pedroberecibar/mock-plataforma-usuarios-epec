import { useEffect, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import { evaluarVencimiento, fetchFacturaDatos } from "../api/factura";
import type { FacturaDatosResponse } from "../api/types";
import {
  bg, border, brand, color, fg,
  font, fontSize, fontWeight, radius, shadow, space,
} from "../design-tokens";
import { PageHeader } from "../components/PageHeader";
import { AlertBanner } from "../components/AlertBanner";

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

function textoDiasRestantes(dias: number): string {
  if (dias < 0) return "Vencida";
  if (dias === 0) return "Vence hoy";
  if (dias === 1) return "Vence mañana";
  return `Faltan ${dias} días`;
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

  const fechaVcto = facturaDatos?.fecha_vencimiento ?? null;
  const diasVcto = fechaVcto ? diasHastaVencimiento(fechaVcto) : null;
  const urgente = diasVcto !== null && diasVcto <= 5;

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <PageHeader title="Mi Factura" />

      <main aria-label="factura del cliente">
        <div style={{ maxWidth: 1400, margin: "0 auto", padding: `${space[10]}px` }}>

          {/* Banner de urgencia — solo cuando faltan <= 5 días */}
          {urgente && fechaVcto && (
            <div style={{ marginBottom: space[4] }}>
              <AlertBanner variant="warning" data-testid="banner-vencimiento">
                ⚠️ Tu factura vence el{" "}
                <strong>{formatFechaVcto(fechaVcto)}</strong>
                {diasVcto === 0
                  ? " — ¡hoy!"
                  : diasVcto === 1
                    ? " — ¡mañana!"
                    : ` (en ${diasVcto} días)`}
                . Recordá abonarla para evitar inconvenientes.
              </AlertBanner>
            </div>
          )}

          {/* Row 1 — Tu factura: importe, vencimiento y pago (hero a todo el ancho) */}
          <VencimientoHero
            fechaVcto={fechaVcto}
            diasVcto={diasVcto}
            urgente={urgente}
            importe={facturaDatos?.importe ?? null}
            periodo={facturaDatos?.periodo ?? null}
            urlPdf={facturaDatos?.url_pdf ?? null}
          />

          {/* Row 2 — Conceptos de tu factura */}
          <ConceptosCard expandido={expandido} onToggle={setExpandido} />
        </div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Row 1 — Próximo vencimiento
// ---------------------------------------------------------------------------
function formatImporte(importe: number): string {
  return importe.toLocaleString("es-AR", {
    style: "currency",
    currency: "ARS",
    minimumFractionDigits: 2,
  });
}

function VencimientoHero({
  fechaVcto, diasVcto, urgente, importe, periodo, urlPdf,
}: {
  fechaVcto: string | null;
  diasVcto: number | null;
  urgente: boolean;
  importe: number | null;
  periodo: string | null;
  urlPdf: string | null;
}) {
  const hayFactura = fechaVcto !== null && diasVcto !== null;
  return (
    <section
      aria-label="Tu factura"
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
      {/* Datos de la factura */}
      <div style={{ minWidth: 240 }}>
        <Label>{periodo ? `Tu factura · ${periodo}` : "Tu factura"}</Label>

        {hayFactura ? (
          <>
            {importe !== null ? (
              <p style={{
                margin:        `${space[2]}px 0 0`,
                fontFamily:    font.technical,
                fontSize:      fontSize["3xl"],
                fontWeight:    fontWeight.light,
                color:         fg.primary,
                lineHeight:    1.1,
                letterSpacing: "-0.02em",
              }}>
                {formatImporte(importe)}
              </p>
            ) : null}

            <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: space[3], marginTop: space[3] }}>
              <span data-testid="fecha-vencimiento" style={{ fontSize: fontSize.sm, color: fg.secondary }}>
                Vence el <strong style={{ color: fg.primary }}>{formatFechaVcto(fechaVcto)}</strong>
              </span>
              <span style={{
                display:      "inline-block",
                padding:      `${space[1]}px ${space[3]}px`,
                borderRadius: radius.full,
                fontSize:     fontSize.sm,
                fontWeight:   fontWeight.semibold,
                background:   urgente ? color.warningLight : bg.selected,
                color:        urgente ? color.warningDark : fg.secondary,
              }}>
                {textoDiasRestantes(diasVcto)}
              </span>
            </div>
          </>
        ) : (
          <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.md, color: fg.muted }}>
            No tenés facturas pendientes de pago.
          </p>
        )}
      </div>

      {/* Acciones */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: space[3], alignItems: "center" }}>
        {urlPdf && (
          <a
            href={urlPdf}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontSize:       fontSize.sm,
              fontWeight:     fontWeight.semibold,
              color:          fg.link,
              textDecoration: "none",
              padding:        `${space[3]}px ${space[4]}px`,
            }}
          >
            Ver factura (PDF)
          </a>
        )}
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
            padding:        `${space[3]}px ${space[6]}px`,
            fontSize:       fontSize.base,
            fontWeight:     fontWeight.semibold,
            fontFamily:     font.sans,
            textDecoration: "none",
            whiteSpace:     "nowrap",
          }}
        >
          Pagar mi factura
        </a>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Row 2a — Conceptos de tu factura (acordeón en una sola card)
// ---------------------------------------------------------------------------
function ConceptosCard({
  expandido, onToggle,
}: { expandido: number | null; onToggle: (i: number | null) => void }) {
  return (
    <Card>
      <Label>Conceptos de tu factura</Label>
      <p style={{ fontSize: fontSize.sm, color: fg.secondary, margin: `${space[2]}px 0 ${space[4]}px`, lineHeight: 1.5 }}>
        Tu factura EPEC se mide en kWh. Estos son los conceptos que la componen:
      </p>
      <div>
        {CONCEPTOS.map((c, i) => {
          const abierto = expandido === i;
          return (
            <div
              key={c.titulo}
              style={{ borderTop: i === 0 ? "none" : `1px solid ${border.default}` }}
            >
              <button
                onClick={() => onToggle(abierto ? null : i)}
                aria-expanded={abierto}
                style={{
                  display:        "flex",
                  alignItems:     "center",
                  justifyContent: "space-between",
                  width:          "100%",
                  background:     "none",
                  border:         "none",
                  cursor:         "pointer",
                  padding:        `${space[3]}px 0`,
                  fontFamily:     font.sans,
                  fontSize:       fontSize.base,
                  fontWeight:     fontWeight.medium,
                  color:          fg.primary,
                  textAlign:      "left",
                }}
              >
                {c.titulo}
                <ChevronIcon open={abierto} />
              </button>
              {abierto && (
                <p style={{
                  margin:     `0 0 ${space[3]}px`,
                  fontSize:   fontSize.sm,
                  color:      fg.secondary,
                  lineHeight: 1.5,
                  maxWidth:   620,
                }}>
                  {c.descripcion}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </Card>
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
// Primitivos compartidos (mismo lenguaje que Objetivos / Consumo)
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
