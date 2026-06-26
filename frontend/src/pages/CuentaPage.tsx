import { useEffect, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import { fetchCuenta } from "../api/cuenta";
import type { CuentaResponse } from "../api/types";
import {
  bg, border, color, fg,
  font, fontSize, fontWeight, radius, shadow, space,
} from "../design-tokens";
import { PageHeader } from "../components/PageHeader";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";

interface Props {
  token: string;
}

type Estado =
  | { tag: "cargando" }
  | { tag: "ok"; cuenta: CuentaResponse }
  | { tag: "sin_datos" }
  | { tag: "no_configurado" }
  | { tag: "error" };

const PLACEHOLDER = "No informado";

function formatFechaISO(iso: string | null): string | null {
  if (!iso) return null;
  const [y, m, d] = iso.split("-");
  if (!y || !m || !d) return iso;
  const meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
  return `${parseInt(d)} de ${meses[parseInt(m) - 1]} de ${y}`;
}

export function CuentaPage({ token }: Props) {
  const [estado, setEstado] = useState<Estado>({ tag: "cargando" });

  useEffect(() => {
    let cancelled = false;
    setEstado({ tag: "cargando" });
    fetchCuenta(token)
      .then((cuenta) => {
        if (!cancelled) setEstado({ tag: "ok", cuenta });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const msg = err instanceof Error ? err.message : "";
        if (msg === "no_configurado") setEstado({ tag: "no_configurado" });
        else if (msg === "sin_datos") setEstado({ tag: "sin_datos" });
        else setEstado({ tag: "error" });
      });
    return () => { cancelled = true; };
  }, [token]);

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <PageHeader title="Mi cuenta" />

      <main aria-label="datos de la cuenta del cliente">
        <div style={{ maxWidth: 1400, margin: "0 auto", padding: `${space[10]}px` }}>

          {estado.tag === "cargando" && (
            <>
              <LoadingSkeleton variant="card" />
              <div style={{ height: space[6] }} />
              <LoadingSkeleton variant="card" count={2} />
            </>
          )}

          {estado.tag === "no_configurado" && (
            <EmptyState
              title="Tus datos no están disponibles por ahora"
              description="Esta sección se conecta con los sistemas de EPEC, que en este momento no están disponibles. Probá de nuevo en unos minutos."
            />
          )}

          {estado.tag === "sin_datos" && (
            <EmptyState
              title="No encontramos datos de tu suministro"
              description="No pudimos recuperar la información de tu cuenta. Si el problema continúa, comunicate con EPEC."
            />
          )}

          {estado.tag === "error" && (
            <EmptyState
              title="No pudimos cargar tus datos"
              description="Ocurrió un error al obtener la información de tu cuenta. Probá de nuevo más tarde."
            />
          )}

          {estado.tag === "ok" && <CuentaContenido cuenta={estado.cuenta} />}
        </div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Contenido — hero de identidad + grilla de 4 cards + nota
// ---------------------------------------------------------------------------
function CuentaContenido({ cuenta }: { cuenta: CuentaResponse }) {
  const { personales, suministro, tarifa, medidor } = cuenta;

  return (
    <>
      {/* Row 1 — Hero de identidad */}
      <IdentidadHero personales={personales} suministro={suministro} />

      {/* Row 2 — Grilla de 4 secciones */}
      <div style={{
        display:             "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
        gap:                 space[4],
        marginBottom:        space[4],
      }}>
        <Card>
          <CardSectionHeader icon={<IconUser />}>Datos personales</CardSectionHeader>
          <DefinitionRow label="Nombre o razón social" value={personales.nombre_o_razon_social} />
          <DefinitionRow label="Tipo de documento" value={personales.tipo_documento} />
          <DefinitionRow label="Documento" value={personales.nro_documento_masked} mono />
          <DefinitionRow label="CUIT" value={personales.cuit_masked} mono />
          <DefinitionRow label="Email" value={personales.email} isLast />
        </Card>

        <Card>
          <CardSectionHeader icon={<IconBolt />}>Suministro</CardSectionHeader>
          <DefinitionRow label="N° de suministro" value={suministro.numero} mono />
          <DefinitionRow label="Estado del servicio" value={suministro.estado_servicio} chip />
          <DefinitionRow label="Dirección" value={suministro.direccion} />
          <DefinitionRow label="Barrio" value={suministro.barrio} />
          <DefinitionRow label="Localidad" value={suministro.localidad} />
          <DefinitionRow label="Código postal" value={suministro.cp} isLast />
        </Card>

        <Card>
          <CardSectionHeader icon={<IconTag />}>Tarifa</CardSectionHeader>
          <DefinitionRow label="Tarifa" value={tarifa.descripcion} />
          <DefinitionRow label="Código" value={tarifa.codigo} mono />
          <DefinitionRow label="Grupo tarifario" value={tarifa.grupo_tarifario} />
          <DefinitionRow label="Clase" value={tarifa.clase_descripcion ?? tarifa.clase} />
          <DefinitionRow label="Tensión" value={tarifa.tension} isLast />
        </Card>

        <Card>
          <CardSectionHeader icon={<IconGauge />}>Medidor</CardSectionHeader>
          <DefinitionRow label="N° de medidor" value={medidor.numero} mono />
          <DefinitionRow label="Marca" value={medidor.marca} />
          <DefinitionRow label="Fase" value={medidor.fase} />
          <DefinitionRow
            label="Medidor inteligente desde"
            value={formatFechaISO(medidor.inteligente_desde)}
            isLast
          />
        </Card>
      </div>

      {/* Row 3 — Nota informativa */}
      <div style={infoNoticeStyle}>
        <IconInfo />
        <span style={{ fontSize: fontSize.sm, color: fg.secondary, lineHeight: 1.5 }}>
          Estos son los datos que EPEC tiene registrados sobre vos. Por tu seguridad, el
          documento y el CUIT se muestran parcialmente ocultos. Si algún dato no coincide,
          comunicate con EPEC para actualizarlo.
        </span>
      </div>
    </>
  );
}

// ---------------------------------------------------------------------------
// Row 1 — Hero de identidad
// ---------------------------------------------------------------------------
function IdentidadHero({
  personales, suministro,
}: {
  personales: CuentaResponse["personales"];
  suministro: CuentaResponse["suministro"];
}) {
  const nombre = personales.nombre_o_razon_social ?? "Cliente EPEC";
  const inicial = (personales.nombre_o_razon_social ?? "E").trim().charAt(0).toUpperCase();

  return (
    <section
      aria-label="Identidad del cliente"
      style={{
        display:      "flex",
        flexWrap:     "wrap",
        gap:          space[6],
        alignItems:   "center",
        background:   bg.surfaceFeat,
        borderRadius: `${radius.lg}px`,
        boxShadow:    shadow.sm,
        padding:      `${space[6]}px`,
        marginBottom: space[4],
        fontFamily:   font.sans,
      }}
    >
      {/* Avatar con inicial */}
      <div
        aria-hidden="true"
        style={{
          width:          64,
          height:         64,
          borderRadius:   radius.full,
          background:     color.green100,
          color:          fg.link,
          display:        "flex",
          alignItems:     "center",
          justifyContent: "center",
          fontFamily:     font.technical,
          fontSize:       fontSize.xl,
          fontWeight:     fontWeight.semibold,
          flexShrink:     0,
        }}
      >
        {inicial}
      </div>

      <div style={{ minWidth: 240, flex: 1 }}>
        <Label>Titular de la cuenta</Label>
        <p style={{
          margin:        `${space[2]}px 0 0`,
          fontFamily:    font.technical,
          fontSize:      fontSize["2xl"],
          fontWeight:    fontWeight.light,
          color:         fg.primary,
          lineHeight:    1.15,
          letterSpacing: "-0.01em",
        }}>
          {nombre}
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: space[3], marginTop: space[2] }}>
          <span style={{ fontFamily: font.technical, fontSize: fontSize.sm, fontWeight: fontWeight.bold, color: fg.link }}>
            {suministro.numero}
          </span>
          {suministro.estado_servicio && (
            <span style={estadoChipStyle(suministro.estado_servicio)}>
              {suministro.estado_servicio}
            </span>
          )}
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// DefinitionRow — fila clave / valor (con placeholder para null)
// ---------------------------------------------------------------------------
function DefinitionRow({
  label, value, mono, chip, isLast,
}: {
  label: string;
  value: string | null | undefined;
  mono?: boolean;
  chip?: boolean;
  isLast?: boolean;
}) {
  const ausente = value === null || value === undefined || value === "";
  return (
    <div style={{
      display:        "flex",
      alignItems:     "baseline",
      justifyContent: "space-between",
      gap:            space[4],
      padding:        `${space[3]}px 0`,
      borderBottom:   isLast ? "none" : `1px solid ${border.default}`,
    }}>
      <span style={{
        fontSize:   fontSize.sm,
        color:      fg.secondary,
        flexShrink: 0,
      }}>
        {label}
      </span>
      {ausente ? (
        <span style={{ fontSize: fontSize.sm, color: fg.muted, fontStyle: "italic", textAlign: "right" }}>
          {PLACEHOLDER}
        </span>
      ) : chip ? (
        <span style={estadoChipStyle(value!)}>{value}</span>
      ) : (
        <span style={{
          fontSize:   fontSize.base,
          fontWeight: fontWeight.medium,
          color:      fg.primary,
          fontFamily: mono ? font.technical : font.sans,
          textAlign:  "right",
          wordBreak:  "break-word",
        }}>
          {value}
        </span>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Chip de estado de servicio — verde si activo, neutral si otro
// ---------------------------------------------------------------------------
function estadoChipStyle(estado: string): CSSProperties {
  const activo = /activ|conect|normal|habilit/i.test(estado);
  return {
    display:      "inline-block",
    padding:      `2px ${space[3]}px`,
    borderRadius: radius.full,
    fontSize:     fontSize.xs,
    fontWeight:   fontWeight.semibold,
    background:   activo ? color.green100 : bg.selected,
    color:        activo ? color.successDark : fg.secondary,
    whiteSpace:   "nowrap",
  };
}

// ---------------------------------------------------------------------------
// Primitivos compartidos (mismo lenguaje que Alertas / Objetivos / Factura)
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

function CardSectionHeader({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <div style={{
      display:      "flex",
      alignItems:   "center",
      gap:          space[2],
      paddingBottom: space[3],
      marginBottom:  space[2],
      borderBottom:  `1px solid ${border.default}`,
    }}>
      {icon}
      <span style={{
        fontFamily:    font.sans,
        fontSize:      fontSize.xs,
        fontWeight:    fontWeight.semibold,
        color:         fg.secondary,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
      }}>
        {children}
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------
function IconUser() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ color: fg.link, flexShrink: 0 }}>
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

function IconBolt() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ color: fg.link, flexShrink: 0 }}>
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  );
}

function IconTag() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ color: fg.link, flexShrink: 0 }}>
      <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
      <line x1="7" y1="7" x2="7.01" y2="7" />
    </svg>
  );
}

function IconGauge() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ color: fg.link, flexShrink: 0 }}>
      <path d="M12 14l4-4" />
      <path d="M3.34 19a10 10 0 1 1 17.32 0" />
    </svg>
  );
}

function IconInfo() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
      style={{ color: fg.muted, flexShrink: 0, marginTop: 2 }}>
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------
const infoNoticeStyle: CSSProperties = {
  display:      "flex",
  alignItems:   "flex-start",
  gap:          space[2],
  padding:      `${space[4]}px ${space[5]}px`,
  background:   bg.surfaceFeat,
  borderRadius: radius.lg,
  boxShadow:    shadow.sm,
};
