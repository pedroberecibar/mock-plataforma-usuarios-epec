import type React from "react";
import type { ReactNode } from "react";
import type { ObjetivoResponse } from "../api/objetivos";
import type { ObjetivoEstadoResponse } from "../api/types";
import { bg, color, fg, font, fontSize, fontWeight, radius, shadow, space } from "../design-tokens";

interface Props {
  objetivo: ObjetivoResponse | null;
  estado: ObjetivoEstadoResponse | null;
  onEditar: () => void;
}

const WARN_THRESHOLD = 0.8;

// Tonos semánticos atenuados (sin gradientes) — alineados a la paleta de Consumo.
type Semantica = "bien" | "aviso" | "superado";
const SEMANTICA: Record<Semantica, { fill: string; text: string; chipBg: string }> = {
  bien:     { fill: "rgba(49,105,72,0.55)",  text: color.green700, chipBg: "rgba(18,78,47,0.10)"   },
  aviso:    { fill: "rgba(193,120,10,0.45)", text: "#8a5a08",      chipBg: "rgba(230,145,10,0.10)" },
  superado: { fill: "rgba(186,26,26,0.40)",  text: color.errorDark, chipBg: "rgba(192,57,43,0.10)" },
};

const CHIP_MENSAJE: Record<string, string> = {
  bajo_ritmo:  "Vas bien, por debajo de tu ritmo objetivo",
  en_ritmo:    "Vas en línea con tu objetivo",
  sobre_ritmo: "Consumís más rápido que tu objetivo",
  agotado:     "Objetivo superado",
};

function mesActualLabel(): string {
  return new Date().toLocaleDateString("es-AR", { month: "long" });
}

function diasDelMesActual(): number {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
}

export function ObjetivoResumenCard({ objetivo, estado, onEditar }: Props) {
  const consumoActual =
    estado && estado.dias_objetivo_consumidos != null && estado.consumo_diario_objetivo_kwh != null
      ? estado.dias_objetivo_consumidos * estado.consumo_diario_objetivo_kwh
      : null;

  const pct =
    objetivo && estado?.objetivo_kwh && consumoActual !== null
      ? Math.min(consumoActual / estado.objetivo_kwh, 1)
      : null;

  const superado = estado?.texto_dinamico === "agotado";
  const enAviso = pct !== null && pct >= WARN_THRESHOLD && !superado;

  const semantica: Semantica = superado
    ? "superado"
    : enAviso || estado?.texto_dinamico === "sobre_ritmo"
      ? "aviso"
      : "bien";
  const sem = SEMANTICA[semantica];

  const sinObjetivo = !objetivo;

  return (
    <section
      aria-label="Objetivo de consumo"
      style={{
        background:   bg.surfaceFeat,
        borderRadius: `${radius.lg}px`,
        boxShadow:    shadow.sm,
        fontFamily:   font.sans,
        marginBottom: space[6],
        display:      "flex",
        flexWrap:     "wrap",
        alignItems:   "stretch",
      }}
    >
      {/* Segmento 1 — Objetivo hero + link editar */}
      <Segmento flex={1.4} first>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: space[2] }}>
          <Label>{`Tu objetivo de ${mesActualLabel()}`}</Label>
          <button onClick={onEditar} style={linkStyle}>
            {sinObjetivo ? "Definir objetivo" : "Editar objetivo"}
          </button>
        </div>
        {sinObjetivo ? (
          <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.md, color: fg.muted }}>
            Sin objetivo definido
          </p>
        ) : (
          <p style={{
            margin:        `${space[1]}px 0 0`,
            fontFamily:    font.technical,
            fontSize:      fontSize["2xl"],
            fontWeight:    fontWeight.light,
            color:         fg.link,
            lineHeight:    1.2,
            letterSpacing: "-0.02em",
          }}>
            {objetivo.valor_kwh}
            <span style={{ fontFamily: font.sans, fontSize: fontSize.sm, fontWeight: fontWeight.regular, color: fg.muted, marginLeft: space[1] }}>
              kWh / mes
            </span>
          </p>
        )}
      </Segmento>

      {sinObjetivo ? (
        <Segmento flex={3.6}>
          <p style={{ margin: 0, fontSize: fontSize.sm, color: fg.secondary, alignSelf: "center" }}>
            Definí una meta mensual para ver tu progreso, ritmo de consumo y comparación con tu zona.
          </p>
        </Segmento>
      ) : (
        <>
          {/* Segmento 2 — Progreso del mes */}
          <Segmento flex={1.6}>
            <Label>Progreso del mes</Label>
            {pct !== null && estado?.objetivo_kwh && consumoActual !== null ? (
              <>
                <div
                  role="progressbar"
                  aria-valuenow={Math.round(pct * 100)}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label="Consumo vs objetivo"
                  style={{ marginTop: space[2], height: 10, background: bg.selected, borderRadius: radius.full, overflow: "hidden" }}
                >
                  <div style={{
                    height:       "100%",
                    width:        `${Math.round(pct * 100)}%`,
                    background:   sem.fill,
                    borderRadius: radius.full,
                    transition:   "width 600ms cubic-bezier(0.34, 1.56, 0.64, 1)",
                  }} />
                </div>
                <p style={{ fontSize: fontSize.xs, color: fg.muted, marginTop: space[1] }}>
                  {Math.round(consumoActual)} de {estado.objetivo_kwh} kWh ({Math.round(pct * 100)}%)
                </p>
              </>
            ) : (
              <p style={{ marginTop: space[2], fontSize: fontSize.xs, color: fg.muted }}>Sin datos de consumo aún</p>
            )}
            {(superado || enAviso || estado?.texto_dinamico === "sobre_ritmo") ? (
              <p role="alert" style={chipStyle(sem)}>
                {superado
                  ? CHIP_MENSAJE.agotado
                  : enAviso
                    ? `Ya consumiste el ${Math.round((pct ?? 0) * 100)}% del objetivo`
                    : CHIP_MENSAJE.sobre_ritmo}
              </p>
            ) : (
              estado && estado.texto_dinamico !== "sin_objetivo" && (
                <p style={chipStyle(sem)}>{CHIP_MENSAJE[estado.texto_dinamico] ?? ""}</p>
              )
            )}
          </Segmento>

          {/* Segmento 3 — kWh restantes / ritmo diario */}
          <Segmento flex={1}>
            <RestantesSegmento objetivo={objetivo} estado={estado} superado={superado} sem={sem} />
          </Segmento>

          {/* Segmento 4 — vs zona */}
          <Segmento flex={1}>
            <Label>Tu objetivo vs tu zona</Label>
            {estado && estado.promedio_vecinos_kwh != null && estado.diferencia_pct != null ? (
              <>
                <span style={{
                  display:      "inline-block",
                  marginTop:    space[2],
                  padding:      `${space[1]}px ${space[3]}px`,
                  borderRadius: radius.full,
                  fontSize:     fontSize.sm,
                  fontWeight:   fontWeight.semibold,
                  background:   estado.diferencia_pct > 0 ? SEMANTICA.superado.chipBg : SEMANTICA.bien.chipBg,
                  color:        estado.diferencia_pct > 0 ? color.errorDark : color.green700,
                }}>
                  {estado.diferencia_pct > 0 ? "+" : ""}{estado.diferencia_pct.toFixed(1)}% vs zona
                </span>
                <p style={{ fontSize: fontSize.xs, color: fg.muted, marginTop: space[1] }}>
                  {estado.n_vecinos} vecinos · promedio {Math.round(estado.promedio_vecinos_kwh)} kWh
                </p>
              </>
            ) : (
              <p style={{ marginTop: space[2], fontSize: fontSize.xs, color: fg.muted }}>
                Sin datos suficientes de tu zona
              </p>
            )}
          </Segmento>
        </>
      )}
    </section>
  );
}

function RestantesSegmento({
  objetivo,
  estado,
  superado,
  sem,
}: {
  objetivo: ObjetivoResponse;
  estado: ObjetivoEstadoResponse | null;
  superado: boolean;
  sem: { fill: string; text: string; chipBg: string };
}) {
  if (superado && estado?.excedente_kwh != null) {
    return (
      <>
        <Label>Excedente</Label>
        <ValorHero value={`${estado.excedente_kwh.toFixed(0)} kWh`} accent={sem.text} />
        <p style={{ margin: 0, fontSize: fontSize.xs, color: fg.muted }}>por encima del objetivo</p>
      </>
    );
  }

  const diasRestantes = estado ? Math.max(0, diasDelMesActual() - estado.dias_transcurridos) : 0;
  const acumulado = estado?.consumo_acumulado_kwh ?? 0;
  const kwhRestantes = Math.max(0, objetivo.valor_kwh - acumulado);
  const kwhPorDia = diasRestantes > 0 ? kwhRestantes / diasRestantes : null;

  return (
    <>
      <Label>kWh restantes</Label>
      <ValorHero value={`${kwhRestantes.toFixed(0)} kWh`} accent={kwhRestantes <= 0 ? color.errorDark : color.green700} />
      <p style={{ margin: 0, fontSize: fontSize.xs, color: fg.muted }}>
        {kwhPorDia !== null
          ? `podés usar ${kwhPorDia.toFixed(1)} kWh/día · ${diasRestantes} días`
          : "para cumplir el objetivo"}
      </p>
    </>
  );
}

// ---------------------------------------------------------------------------
// Sub-componentes de presentación
// ---------------------------------------------------------------------------
function Segmento({ children, flex, first }: { children: ReactNode; flex: number; first?: boolean }) {
  return (
    <div style={{
      flex:       `${flex} 1 200px`,
      display:    "flex",
      flexDirection: "column",
      padding:    `${space[5]}px`,
      borderLeft: first ? undefined : "1px solid rgba(180,140,80,0.18)",
    }}>
      {children}
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

function ValorHero({ value, accent }: { value: string; accent: string }) {
  return (
    <p style={{
      margin:     `${space[1]}px 0`,
      fontFamily: font.technical,
      fontSize:   fontSize.md,
      fontWeight: fontWeight.bold,
      color:      accent,
      lineHeight: 1.2,
    }}>
      {value}
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
    margin:       `${space[2]}px 0 0`,
    padding:      `${space[1]}px ${space[3]}px`,
    borderRadius: radius.sm,
    fontSize:     fontSize.xs,
    fontWeight:   fontWeight.medium,
    background:   sem.chipBg,
    color:        sem.text,
  };
}
