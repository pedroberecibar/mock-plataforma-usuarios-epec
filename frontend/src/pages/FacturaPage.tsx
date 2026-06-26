import { useEffect, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import { evaluarVencimiento, fetchFacturaDatos } from "../api/factura";
import type { FacturaDatosResponse, FacturaDocumento } from "../api/types";
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

function formatImporte(importe: number): string {
  return importe.toLocaleString("es-AR", {
    style: "currency",
    currency: "ARS",
    minimumFractionDigits: 2,
  });
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

  const documentos = facturaDatos?.documentos ?? [];
  const totalDeuda = facturaDatos?.total_deuda ?? 0;
  const hayDeuda = documentos.length > 0;

  // Vencimiento más próximo (el más urgente) para el banner de aviso.
  const diasList = documentos
    .map((d) => (d.fecha_vencimiento ? diasHastaVencimiento(d.fecha_vencimiento) : null))
    .filter((d): d is number => d !== null);
  const minDias = diasList.length ? Math.min(...diasList) : null;
  const proximaFecha = documentos
    .filter((d) => d.fecha_vencimiento)
    .sort((a, b) =>
      diasHastaVencimiento(a.fecha_vencimiento!) - diasHastaVencimiento(b.fecha_vencimiento!))[0]
    ?.fecha_vencimiento ?? null;
  const urgente = minDias !== null && minDias <= 5;

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <PageHeader title="Mi Factura" />

      <main aria-label="factura del cliente">
        <div style={{ maxWidth: 1400, margin: "0 auto", padding: `${space[10]}px` }}>

          {/* Banner de urgencia — el vencimiento más próximo está a <= 5 días */}
          {urgente && proximaFecha && minDias !== null && (
            <div style={{ marginBottom: space[4] }}>
              <AlertBanner variant="warning" data-testid="banner-vencimiento">
                ⚠️{" "}
                {minDias < 0 ? (
                  <>Tenés una factura <strong>vencida</strong> ({formatFechaVcto(proximaFecha)}).</>
                ) : (
                  <>
                    Tu próxima factura vence el <strong>{formatFechaVcto(proximaFecha)}</strong>
                    {minDias === 0 ? " — ¡hoy!" : minDias === 1 ? " — ¡mañana!" : ` (en ${minDias} días)`}.
                  </>
                )}{" "}
                Recordá abonarla para evitar inconvenientes.
              </AlertBanner>
            </div>
          )}

          {/* Row 1 — Deuda total + acción de pago */}
          <DeudaHero
            total={totalDeuda}
            hayDeuda={hayDeuda}
            cantidad={documentos.length}
          />

          {/* Row 2 — Listado de facturas */}
          {hayDeuda && (
            <section aria-label="Facturas a pagar" style={{ marginBottom: space[4] }}>
              <Label>{documentos.length === 1 ? "Tu factura" : "Tus facturas"}</Label>
              <div style={{ display: "flex", flexDirection: "column", gap: space[3], marginTop: space[3] }}>
                {documentos.map((d, i) => (
                  <FacturaItemCard key={d.periodo ?? i} doc={d} />
                ))}
              </div>
            </section>
          )}

          {/* Row 3 — Conceptos de tu factura */}
          <ConceptosCard expandido={expandido} onToggle={setExpandido} />
        </div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Row 1 — Deuda total + botón de pago
// ---------------------------------------------------------------------------
function DeudaHero({ total, hayDeuda, cantidad }: { total: number; hayDeuda: boolean; cantidad: number }) {
  return (
    <section
      aria-label="Deuda total"
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
        <Label>Deuda total</Label>
        {hayDeuda ? (
          <>
            <p style={{
              margin:        `${space[2]}px 0 0`,
              fontFamily:    font.technical,
              fontSize:      fontSize["3xl"],
              fontWeight:    fontWeight.light,
              color:         fg.primary,
              lineHeight:    1.1,
              letterSpacing: "-0.02em",
            }}>
              {formatImporte(total)}
            </p>
            <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.sm, color: fg.secondary }}>
              {cantidad === 1 ? "1 factura pendiente" : `${cantidad} facturas pendientes`}
            </p>
          </>
        ) : (
          <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.md, color: fg.muted }}>
            No tenés facturas pendientes de pago.
          </p>
        )}
      </div>

      {hayDeuda && (
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
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Card compacta por factura
// ---------------------------------------------------------------------------
function estadoChip(estado: string | null, dias: number | null): { bg: string; color: string } {
  if (estado?.toLowerCase() === "vencida" || (dias !== null && dias < 0)) {
    return { bg: color.errorLight, color: color.errorDark };
  }
  if (dias !== null && dias <= 5) {
    return { bg: color.warningLight, color: color.warningDark };
  }
  return { bg: color.green100, color: color.successDark };
}

function FacturaItemCard({ doc }: { doc: FacturaDocumento }) {
  const dias = doc.fecha_vencimiento ? diasHastaVencimiento(doc.fecha_vencimiento) : null;
  const chip = estadoChip(doc.estado, dias);
  return (
    <div style={{
      display:        "flex",
      flexWrap:       "wrap",
      gap:            space[4],
      alignItems:     "center",
      justifyContent: "space-between",
      background:     bg.surface,
      borderRadius:   `${radius.md}px`,
      boxShadow:      shadow.xs,
      padding:        `${space[4]}px ${space[5]}px`,
    }}>
      {/* Período + vencimiento */}
      <div style={{ minWidth: 180 }}>
        <p style={{ margin: 0, fontSize: fontSize.base, fontWeight: fontWeight.semibold, color: fg.primary }}>
          {doc.periodo ? `Período ${doc.periodo}` : "Factura"}
        </p>
        {doc.fecha_vencimiento && (
          <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: space[2], marginTop: space[1] }}>
            <span style={{ fontSize: fontSize.xs, color: fg.muted }}>
              Vence el {formatFechaVcto(doc.fecha_vencimiento)}
            </span>
            <span style={{
              padding:      `2px ${space[2]}px`,
              borderRadius: radius.full,
              fontSize:     fontSize.xs,
              fontWeight:   fontWeight.semibold,
              background:   chip.bg,
              color:        chip.color,
            }}>
              {dias !== null ? textoDiasRestantes(dias) : doc.estado}
            </span>
          </div>
        )}
      </div>

      {/* Importe + PDF */}
      <div style={{ display: "flex", alignItems: "center", gap: space[5] }}>
        {doc.importe !== null && (
          <span style={{
            fontFamily: font.technical,
            fontSize:   fontSize.lg,
            fontWeight: fontWeight.bold,
            color:      fg.primary,
          }}>
            {formatImporte(doc.importe)}
          </span>
        )}
        {doc.url_pdf && (
          <a
            href={doc.url_pdf}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontSize:       fontSize.sm,
              fontWeight:     fontWeight.semibold,
              color:          fg.link,
              textDecoration: "none",
              whiteSpace:     "nowrap",
            }}
          >
            Ver PDF
          </a>
        )}
      </div>
    </div>
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
