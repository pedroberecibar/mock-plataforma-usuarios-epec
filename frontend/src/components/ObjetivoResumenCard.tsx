import type React from "react";
import type { ReactNode } from "react";
import type { ObjetivoResponse } from "../api/objetivos";
import type { ObjetivoEstadoResponse } from "../api/types";
import { bg, color, fg, font, fontSize, fontWeight, radius, shadow, space } from "../design-tokens";

interface Props {
  objetivo: ObjetivoResponse | null;
  consumoActualKwh: number | null;
  estado: ObjetivoEstadoResponse | null;
  /** Nombre del mes mostrado (ej. "junio"). Por defecto, el mes actual. */
  mesLabel?: string;
  onEditar: () => void;
}

const WARN_THRESHOLD = 0.8;

// Tonos semánticos atenuados (sin gradientes) — alineados a la paleta de Consumo.
type Semantica = "bien" | "aviso" | "superado";
const SEMANTICA: Record<Semantica, { fill: string; text: string; chipBg: string }> = {
  bien:     { fill: "rgba(49,105,72,0.55)",  text: color.green700,  chipBg: "rgba(18,78,47,0.10)"   },
  aviso:    { fill: "rgba(193,120,10,0.45)", text: "#8a5a08",       chipBg: "rgba(230,145,10,0.10)" },
  superado: { fill: "rgba(186,26,26,0.40)",  text: color.errorDark, chipBg: "rgba(192,57,43,0.10)"  },
};

function mesActualLabel(): string {
  return new Date().toLocaleDateString("es-AR", { month: "long" });
}

function fmtKwh(value: number): string {
  return `${Math.round(value)} kWh`;
}

export function ObjetivoResumenCard({ objetivo, consumoActualKwh, estado, mesLabel, onEditar }: Props) {
  const sinObjetivo = !objetivo;

  const pct =
    objetivo && consumoActualKwh != null
      ? Math.min(consumoActualKwh / objetivo.valor_kwh, 1)
      : null;

  const diff =
    objetivo && consumoActualKwh != null ? objetivo.valor_kwh - consumoActualKwh : null;

  const superado = estado?.texto_dinamico === "agotado" || (diff !== null && diff < 0);
  const enAviso = pct !== null && pct >= WARN_THRESHOLD && !superado;

  const semantica: Semantica = superado
    ? "superado"
    : enAviso || estado?.texto_dinamico === "sobre_ritmo"
      ? "aviso"
      : "bien";
  const sem = SEMANTICA[semantica];

  return (
    <section
      aria-label="Objetivo de consumo"
      style={{
        position:     "relative",
        background:   bg.surfaceFeat,
        borderRadius: `${radius.lg}px`,
        boxShadow:    shadow.sm,
        fontFamily:   font.sans,
        marginBottom: space[6],
        padding:      `${space[5]}px`,
      }}
    >
      {/* Link editar — esquina superior derecha de la card */}
      <button
        onClick={onEditar}
        style={{ ...linkStyle, position: "absolute", top: space[5], right: space[5] }}
      >
        {sinObjetivo ? "Definir objetivo" : "Editar objetivo"}
      </button>

      {/* Fila superior: objetivo, consumo actual y excedente/faltante alineados a la izquierda */}
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-start", gap: space[6], paddingRight: 120 }}>
        {/* Objetivo hero */}
        <div style={{ flex: "0 0 auto" }}>
          <Label>{`Tu objetivo de ${mesLabel ?? mesActualLabel()}`}</Label>
          {sinObjetivo ? (
            <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.md, color: fg.muted }}>
              Sin objetivo definido
            </p>
          ) : (
            <p style={{
              margin:        `${space[1]}px 0 0`,
              fontFamily:    font.technical,
              fontSize:      fontSize["3xl"],
              fontWeight:    fontWeight.light,
              color:         fg.link,
              lineHeight:    1.1,
              letterSpacing: "-0.02em",
            }}>
              {objetivo.valor_kwh}
              <span style={{ fontFamily: font.sans, fontSize: fontSize.sm, fontWeight: fontWeight.regular, color: fg.muted, marginLeft: space[2] }}>
                kWh / mes
              </span>
            </p>
          )}
        </div>

        {!sinObjetivo && (
          <>
            <Stat
              label="Consumo actual"
              value={consumoActualKwh != null ? fmtKwh(consumoActualKwh) : "—"}
              sub={`de ${objetivo.valor_kwh} kWh`}
            />
            <ExcedenteFaltante estado={estado} diff={diff} superado={superado} sem={sem} />
          </>
        )}
      </div>

      {/* Progreso del mes (kWh) — barra a todo el ancho */}
      {sinObjetivo ? (
        <p style={{ margin: `${space[4]}px 0 0`, fontSize: fontSize.sm, color: fg.secondary }}>
          Definí una meta mensual para ver tu progreso de consumo.
        </p>
      ) : (
        <div style={{ marginTop: space[6] }}>
          <Label>Progreso del mes</Label>
          {pct !== null && consumoActualKwh != null ? (
            <>
              <ProgressBar pct={pct} fill={sem.fill} ariaLabel="Consumo vs objetivo" />
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: space[3], marginTop: space[2], flexWrap: "wrap" }}>
                <p style={{ margin: 0, fontSize: fontSize.xs, color: fg.muted }}>
                  {Math.round(consumoActualKwh)} de {objetivo.valor_kwh} kWh ({Math.round(pct * 100)}%)
                </p>
                {(superado || enAviso || estado?.texto_dinamico === "sobre_ritmo") && (
                  <p role="alert" style={chipStyle(sem)}>
                    {superado
                      ? "Objetivo superado"
                      : enAviso
                        ? `Ya consumiste el ${Math.round(pct * 100)}% del objetivo`
                        : "Consumís más rápido que tu objetivo"}
                  </p>
                )}
              </div>
            </>
          ) : (
            <p style={{ marginTop: space[2], fontSize: fontSize.xs, color: fg.muted }}>Sin datos de consumo aún</p>
          )}

          {/* Días de consumo — como en Objetivos */}
          {estado && estado.dias_objetivo_consumidos != null && estado.dias_transcurridos > 0 && (
            <div style={{ marginTop: space[5] }}>
              <Label>Días de consumo</Label>
              <ProgressBar
                pct={Math.min(estado.dias_objetivo_consumidos / estado.dias_transcurridos, 1)}
                fill={sem.fill}
                ariaLabel="Días objetivo consumidos"
              />
              <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.xs, color: fg.muted }}>
                {estado.dias_objetivo_consumidos.toFixed(1)} de {estado.dias_transcurridos} días objetivo consumidos
              </p>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function ProgressBar({ pct, fill, ariaLabel }: { pct: number; fill: string; ariaLabel: string }) {
  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(pct * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={ariaLabel}
      style={{ width: "100%", marginTop: space[2], height: 12, background: bg.selected, borderRadius: radius.full, overflow: "hidden" }}
    >
      <div style={{
        height:       "100%",
        width:        `${Math.round(pct * 100)}%`,
        background:   fill,
        borderRadius: radius.full,
        transition:   "width 600ms cubic-bezier(0.34, 1.56, 0.64, 1)",
      }} />
    </div>
  );
}

function ExcedenteFaltante({
  estado,
  diff,
  superado,
  sem,
}: {
  estado: ObjetivoEstadoResponse | null;
  diff: number | null;
  superado: boolean;
  sem: { fill: string; text: string; chipBg: string };
}) {
  if (superado) {
    const excedente = estado?.excedente_kwh ?? (diff !== null ? -diff : null);
    return (
      <Stat
        label="Excedente"
        value={excedente != null ? fmtKwh(excedente) : "—"}
        sub="por encima del objetivo"
        accent={sem.text}
      />
    );
  }
  return (
    <Stat
      label="Faltante"
      value={diff != null ? fmtKwh(diff) : "—"}
      sub="para alcanzar el objetivo"
      accent={color.green700}
    />
  );
}

// ---------------------------------------------------------------------------
// Sub-componentes de presentación
// ---------------------------------------------------------------------------
function Stat({ label, value, sub, accent }: { label: string; value: string; sub: string; accent?: string }) {
  return (
    <div style={{ flex: "0 1 auto" }}>
      <Label>{label}</Label>
      <p style={{
        margin:     `${space[1]}px 0`,
        fontFamily: font.technical,
        fontSize:   fontSize.lg,
        fontWeight: fontWeight.bold,
        color:      accent ?? fg.primary,
        lineHeight: 1.2,
      }}>
        {value}
      </p>
      <p style={{ margin: 0, fontSize: fontSize.xs, color: fg.muted }}>{sub}</p>
    </div>
  );
}

function Label({ children }: { children: ReactNode }) {
  return (
    <p style={{
      margin:        0,
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

const linkStyle: React.CSSProperties = {
  background:     "none",
  border:         "none",
  padding:        0,
  color:          fg.link,
  fontFamily:     font.sans,
  fontSize:       fontSize.sm,
  fontWeight:     fontWeight.semibold,
  cursor:         "pointer",
  textDecoration: "none",
  whiteSpace:     "nowrap",
};

function chipStyle(sem: { chipBg: string; text: string }): React.CSSProperties {
  return {
    margin:       0,
    padding:      `${space[1]}px ${space[3]}px`,
    borderRadius: radius.sm,
    fontSize:     fontSize.xs,
    fontWeight:   fontWeight.medium,
    background:   sem.chipBg,
    color:        sem.text,
  };
}
