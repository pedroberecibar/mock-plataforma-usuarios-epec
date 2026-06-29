import { useEffect, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import { bg, border, color, fg, font, fontSize, fontWeight, radius, shadow, space } from "../design-tokens";
import {
  evaluarObjetivo,
  fetchObjetivoEstado,
  fetchObjetivo,
  setObjetivo,
  type ObjetivoResponse,
} from "../api/objetivos";
import type { ObjetivoEstadoResponse } from "../api/types";
import { PageHeader } from "../components/PageHeader";
import { LoadingSkeleton } from "../components/LoadingSkeleton";

interface ObjetivosPageProps {
  token: string;
  suministroId: string;
  onLogout?: () => void;
}

type Estado = "cargando" | "sin_objetivo" | "con_objetivo" | "editando" | "guardando" | "error";

function mesActualYYYYMM(): string {
  const now = new Date();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  return `${now.getFullYear()}-${m}`;
}

function mesActualLabel(): string {
  return new Date().toLocaleDateString("es-AR", { month: "long" });
}

function diasDelMesActual(): number {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
}

// Margen de tolerancia sobre el ritmo lineal antes de pasar a ambar / rojo.
// ritmo = % consumido / % del mes transcurrido (1.0 = exactamente en linea).
// El margen evita falsos rojos sobre el final del mes: consumir 98% faltando
// 1 dia da ritmo ~1.01 (verde); el mismo 98% faltando 10 dias da ~1.47 (rojo).
const RITMO_AVISO = 1.05;  // un poco por encima del ritmo proporcional al tiempo
const RITMO_ALTO = 1.20;   // claramente acelerado respecto del tiempo restante

// ---------------------------------------------------------------------------
// Semantica consolidada — un solo eje de color (verde / ambar / rojo) basado
// en tokens del Design System. Sin gradientes ni rgba sueltos.
// ---------------------------------------------------------------------------
type Semantica = "bien" | "aviso" | "superado";

const SEMANTICA: Record<Semantica, { fill: string; text: string; chipBg: string }> = {
  bien:     { fill: color.green500,   text: color.successDark, chipBg: color.green100 },
  aviso:    { fill: color.warning,    text: color.warningDark, chipBg: color.warningLight },
  superado: { fill: color.error,      text: color.errorDark,   chipBg: color.errorLight },
};

// Semaforo sensible al tiempo: compara cuanto se consumio del objetivo contra
// cuanto del mes transcurrio. Consumir el 98% faltando 1 dia esta "en linea"
// (verde); el mismo 98% faltando 10 dias va muy acelerado (rojo).
function clasificarPorRitmo(
  pctReal: number | null,
  diasTranscurridos: number,
  diasDelMes: number,
): Semantica {
  if (pctReal === null || diasDelMes <= 0 || diasTranscurridos <= 0) return "bien";
  const fraccionMes = Math.min(diasTranscurridos / diasDelMes, 1);
  if (fraccionMes <= 0) return "bien";
  const ritmo = pctReal / fraccionMes; // 1.0 = consumo proporcional al tiempo transcurrido
  if (ritmo > RITMO_ALTO) return "superado";
  if (ritmo > RITMO_AVISO) return "aviso";
  return "bien";
}

export function ObjetivosPage({ token, suministroId, onLogout }: ObjetivosPageProps) {
  const [objetivo, setObjetivoState] = useState<ObjetivoResponse | null>(null);
  const [estado, setEstado] = useState<Estado>("cargando");
  const [inputKwh, setInputKwh] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [estadoObj, setEstadoObj] = useState<ObjetivoEstadoResponse | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const mes = mesActualYYYYMM();
    setEstado("cargando");

    Promise.all([
      fetchObjetivo(token),
      fetchObjetivoEstado(token, mes).catch(() => null),
    ]).then(([obj, est]) => {
      if (cancelled) return;
      setObjetivoState(obj);
      setEstado(obj ? "con_objetivo" : "sin_objetivo");
      if (obj) setInputKwh(String(obj.valor_kwh));
      setEstadoObj(est);
    }).catch((err: unknown) => {
      if (cancelled) return;
      if (err instanceof Error && err.message.includes("401")) {
        onLogout?.();
      } else {
        setEstado("error");
      }
    });

    evaluarObjetivo(token);

    return () => { cancelled = true; };
  }, [token, suministroId, retryCount]);

  async function handleGuardar() {
    const valor = parseFloat(inputKwh);
    if (isNaN(valor) || valor <= 0) {
      setErrorMsg("Ingresá un valor mayor a 0 kWh");
      return;
    }
    setErrorMsg(null);
    setEstado("guardando");
    try {
      const nuevo = await setObjetivo(token, valor);
      setObjetivoState(nuevo);
      setEstado("con_objetivo");
      const mes = mesActualYYYYMM();
      const est = await fetchObjetivoEstado(token, mes).catch(() => null);
      setEstadoObj(est);
    } catch {
      setEstado("error");
    }
  }

  const consumoActual = estadoObj
    ? (estadoObj.dias_objetivo_consumidos != null && estadoObj.consumo_diario_objetivo_kwh != null
        ? estadoObj.dias_objetivo_consumidos * estadoObj.consumo_diario_objetivo_kwh
        : null)
    : null;

  const pct = objetivo && estadoObj?.objetivo_kwh && consumoActual !== null
    ? Math.min(consumoActual / estadoObj.objetivo_kwh, 1)
    : null;

  // Porcentaje real (sin tope) para el semaforo temporal.
  const pctReal = objetivo && estadoObj?.objetivo_kwh && consumoActual !== null
    ? consumoActual / estadoObj.objetivo_kwh
    : null;

  const diasDelMes = diasDelMesActual();
  const diasRestantes = estadoObj
    ? Math.max(0, diasDelMes - estadoObj.dias_transcurridos)
    : 0;

  const nivel = clasificarPorRitmo(pctReal, estadoObj?.dias_transcurridos ?? 0, diasDelMes);
  const sem = SEMANTICA[nivel];

  const tieneDatosMes = !!(estadoObj && estadoObj.texto_dinamico !== "sin_objetivo");

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <PageHeader title="Objetivo de consumo" />

      <main aria-label="objetivo de consumo del cliente">
        <div style={{ maxWidth: 1400, margin: "0 auto", padding: `${space[10]}px` }}>

          {estado === "cargando" && (
            <>
              <LoadingSkeleton variant="card" />
              <div style={{ height: space[6] }} />
              <LoadingSkeleton variant="card" />
            </>
          )}

          {estado === "error" && (
            <div style={{
              display:      "flex",
              alignItems:   "center",
              gap:          space[3],
              padding:      `${space[3]}px ${space[4]}px`,
              background:   color.errorLight,
              borderRadius: radius.md,
            }}>
              <p style={{ color: color.errorDark, fontSize: fontSize.sm, margin: 0, flex: 1 }}>
                Error al cargar el objetivo.
              </p>
              <button
                onClick={() => { setEstadoObj(null); setObjetivoState(null); setRetryCount((n) => n + 1); }}
                style={{
                  padding:      `${space[2]}px ${space[4]}px`,
                  background:   color.errorDark,
                  color:        fg.onDark,
                  border:       "none",
                  borderRadius: radius.sm,
                  fontSize:     fontSize.xs,
                  fontWeight:   fontWeight.medium,
                  cursor:       "pointer",
                  whiteSpace:   "nowrap",
                }}
              >
                Reintentar
              </button>
            </div>
          )}

          {(estado === "con_objetivo" || estado === "sin_objetivo" || estado === "guardando") && (
            <>
              {/* Row 1 — Hero: objetivo vigente a todo el ancho */}
              <HeroObjetivo objetivo={objetivo} />

              {/* Row 2 — Resumen del mes (KPIs), directamente bajo el objetivo */}
              {estadoObj && estadoObj.consumo_acumulado_kwh != null && objetivo && (
                <ResumenMesCard estadoObj={estadoObj} objetivo={objetivo} />
              )}

              {/* Row 3 — Grilla de dos cards: ritmo | consumo acumulado (semaforo temporal) */}
              {tieneDatosMes && (
                <div style={{
                  display:             "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
                  gap:                 space[4],
                  marginBottom:        space[4],
                }}>
                  {estadoObj!.dias_objetivo_consumidos != null && (
                    <RitmoCard estadoObj={estadoObj!} sem={sem} diasRestantes={diasRestantes} />
                  )}
                  {pct !== null && estadoObj?.objetivo_kwh && consumoActual !== null && objetivo && (
                    <ProgresoMesCard
                      pct={pct}
                      consumoActual={consumoActual}
                      objetivoKwh={estadoObj.objetivo_kwh}
                      sem={sem}
                      nivel={nivel}
                      diasRestantes={diasRestantes}
                    />
                  )}
                </div>
              )}

              {/* Row 4 — Card de edición / configuración */}
              <EditorObjetivo
                objetivo={objetivo}
                inputKwh={inputKwh}
                errorMsg={errorMsg}
                guardando={estado === "guardando"}
                onChange={setInputKwh}
                onGuardar={handleGuardar}
              />
            </>
          )}
        </div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Row 1 — Hero objetivo vigente
// ---------------------------------------------------------------------------
function HeroObjetivo({ objetivo }: { objetivo: ObjetivoResponse | null }) {
  return (
    <section
      aria-label="Objetivo vigente"
      style={{
        background:   bg.surfaceFeat,
        borderRadius: `${radius.lg}px`,
        boxShadow:    shadow.sm,
        padding:      `${space[6]}px`,
        marginBottom: space[4],
        fontFamily:   font.sans,
      }}
    >
      <Label>{`Tu objetivo de ${mesActualLabel()}`}</Label>
      {objetivo ? (
        <>
          <p style={{
            margin:        `${space[2]}px 0 0`,
            fontFamily:    font.technical,
            fontSize:      fontSize["3xl"],
            fontWeight:    fontWeight.light,
            color:         fg.link,
            lineHeight:    1.1,
            letterSpacing: "-0.02em",
          }}>
            {objetivo.valor_kwh}
            <span style={{ fontFamily: font.sans, fontSize: fontSize.lg, fontWeight: fontWeight.regular, color: fg.secondary, marginLeft: space[2] }}>
              kWh / mes
            </span>
          </p>
          <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.xs, color: fg.muted }}>
            Configurado el {new Date(objetivo.vigente_desde).toLocaleDateString("es-AR")}
          </p>
        </>
      ) : (
        <p style={{ margin: `${space[2]}px 0 0`, fontSize: fontSize.md, color: fg.muted }}>
          Sin objetivo definido — configurá una meta mensual abajo.
        </p>
      )}
    </section>
  );
}

function Barra({
  etiqueta, valor, valorColor, fill, pct,
}: { etiqueta: string; valor: string; valorColor: string; fill: string; pct: number }) {
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: space[2] }}>
        <span style={{
          fontSize:      fontSize.xs,
          fontWeight:    fontWeight.semibold,
          color:         fg.secondary,
          textTransform: "uppercase",
          letterSpacing: "0.05em",
        }}>
          {etiqueta}
        </span>
        <span style={{ fontSize: fontSize.sm, fontWeight: fontWeight.bold, color: valorColor, fontFamily: font.technical }}>
          {valor}
        </span>
      </div>
      <div style={{ width: "100%", height: 10, background: bg.selected, borderRadius: radius.full, overflow: "hidden" }}>
        <div style={{
          height:       "100%",
          width:        `${Math.round(Math.min(pct, 1) * 100)}%`,
          background:   fill,
          borderRadius: radius.full,
          transition:   "width 600ms cubic-bezier(0.34, 1.56, 0.64, 1)",
        }} />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Row 2b — Ritmo de consumo (días) + mensaje dinámico
// ---------------------------------------------------------------------------
function RitmoCard({
  estadoObj, sem, diasRestantes,
}: {
  estadoObj: ObjetivoEstadoResponse;
  sem: { fill: string; text: string; chipBg: string };
  diasRestantes: number;
}) {
  const { texto_dinamico, dias_objetivo_consumidos, dias_transcurridos, excedente_kwh } = estadoObj;

  const mensajes: Record<string, string> = {
    bajo_ritmo:  "Vas bien, estás por debajo de tu ritmo objetivo.",
    en_ritmo:    "Vas en línea con tu objetivo.",
    sobre_ritmo: "Atención, estás consumiendo más rápido que tu objetivo.",
    agotado:     "Ya alcanzaste tu objetivo de consumo de este mes.",
  };

  const barPct = dias_objetivo_consumidos != null && dias_transcurridos > 0
    ? Math.min(dias_objetivo_consumidos / dias_transcurridos, 1)
    : 0;

  const palanca = texto_dinamico === "sobre_ritmo" || texto_dinamico === "agotado";

  return (
    <Card>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: space[3] }}>
        <Label>Ritmo de consumo</Label>
        <DiasRestantesChip dias={diasRestantes} sem={sem} />
      </div>

      {dias_objetivo_consumidos != null && (
        <div style={{ marginTop: space[4] }}>
          <Barra
            etiqueta="Días transcurridos"
            valor={`${dias_objetivo_consumidos.toFixed(1)} / ${dias_transcurridos}`}
            valorColor={sem.text}
            fill={sem.fill}
            pct={barPct}
          />
        </div>
      )}

      <p
        data-testid="indicador-2-texto"
        style={{
          marginTop:    space[4],
          padding:      `${space[3]}px ${space[4]}px`,
          borderRadius: radius.md,
          fontSize:     fontSize.sm,
          fontWeight:   fontWeight.medium,
          background:   sem.chipBg,
          color:        sem.text,
        }}
      >
        {mensajes[texto_dinamico]}
        {texto_dinamico === "agotado" && excedente_kwh != null && (
          <> Excedente: {excedente_kwh.toFixed(1)} kWh.</>
        )}
      </p>

      {palanca && (
        <p style={{ fontSize: fontSize.xs, color: fg.secondary, marginTop: space[3], lineHeight: 1.5 }}>
          Palanca: revisá tus electrodomésticos de mayor consumo o postponé el uso de
          lavarropas/lavavajillas a horarios de menor demanda.
        </p>
      )}
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Row 3 — Progreso del mes (kWh)
// ---------------------------------------------------------------------------
function ProgresoMesCard({
  pct, consumoActual, objetivoKwh, sem, nivel, diasRestantes,
}: {
  pct: number;
  consumoActual: number;
  objetivoKwh: number;
  sem: { fill: string; text: string; chipBg: string };
  nivel: Semantica;
  diasRestantes: number;
}) {
  const pctTxt = Math.round(pct * 100);

  return (
    <Card>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: space[3] }}>
        <Label>Consumo acumulado este mes</Label>
        <DiasRestantesChip dias={diasRestantes} sem={sem} />
      </div>

      {nivel !== "bien" && (
        <p
          role="alert"
          style={{
            margin:       `${space[3]}px 0`,
            padding:      `${space[2]}px ${space[3]}px`,
            borderRadius: radius.sm,
            fontSize:     fontSize.sm,
            fontWeight:   fontWeight.medium,
            background:   sem.chipBg,
            color:        sem.text,
          }}
        >
          {nivel === "superado"
            ? `Ritmo alto: consumiste el ${pctTxt}% del objetivo y todavía faltan ${diasRestantes} ${diasRestantes === 1 ? "día" : "días"}. A este paso vas a quedar superado.`
            : `Atención: vas un poco acelerado — ${pctTxt}% del objetivo con ${diasRestantes} ${diasRestantes === 1 ? "día" : "días"} por delante.`}
        </p>
      )}

      <div
        role="progressbar"
        aria-valuenow={Math.round(pct * 100)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Progreso consumo vs objetivo"
        style={{
          marginTop:    space[3],
          height:       12,
          background:   bg.selected,
          borderRadius: radius.full,
          overflow:     "hidden",
        }}
      >
        <div style={{
          height:       "100%",
          width:        `${Math.round(pct * 100)}%`,
          background:   sem.fill,
          borderRadius: radius.full,
          transition:   "width 600ms cubic-bezier(0.34, 1.56, 0.64, 1)",
        }} />
      </div>

      <p style={{ fontSize: fontSize.xs, color: fg.muted, marginTop: space[2] }}>
        {Math.round(consumoActual)} de {objetivoKwh} kWh ({Math.round(pct * 100)}%)
      </p>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Row 4 — Resumen del mes (KPIs)
// ---------------------------------------------------------------------------
function ResumenMesCard({
  estadoObj, objetivo,
}: { estadoObj: ObjetivoEstadoResponse; objetivo: ObjetivoResponse }) {
  const diasDelMes = diasDelMesActual();
  const diasRestantes = Math.max(0, diasDelMes - estadoObj.dias_transcurridos);
  const acumulado = estadoObj.consumo_acumulado_kwh ?? 0;
  const kwhRestantes = Math.max(0, objetivo.valor_kwh - acumulado);
  const kwhPorDia = diasRestantes > 0 ? kwhRestantes / diasRestantes : null;

  return (
    <Card style={{ marginBottom: space[4] }}>
      <Label>Resumen del mes</Label>
      <div style={{
        display:             "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
        gap:                 space[3],
        marginTop:           space[4],
      }}>
        {estadoObj.consumo_promedio_diario_kwh != null && (
          <Kpi
            label="Promedio diario"
            value={`${estadoObj.consumo_promedio_diario_kwh.toFixed(1)} kWh`}
            sub="este mes"
          />
        )}
        {estadoObj.consumo_diario_real_kwh != null && estadoObj.consumo_diario_objetivo_kwh != null && (
          <Kpi
            label="Último día vs objetivo"
            value={`${estadoObj.consumo_diario_real_kwh.toFixed(1)} kWh`}
            sub={`objetivo diario ${estadoObj.consumo_diario_objetivo_kwh.toFixed(1)} kWh`}
            accent={estadoObj.consumo_diario_real_kwh <= estadoObj.consumo_diario_objetivo_kwh ? color.successDark : color.errorDark}
          />
        )}
        <Kpi
          label="kWh restantes"
          value={`${kwhRestantes.toFixed(0)} kWh`}
          sub="para cumplir el objetivo"
          accent={kwhRestantes <= 0 ? color.errorDark : color.successDark}
        />
        {kwhPorDia !== null && kwhRestantes > 0 && (
          <Kpi
            label="Podés usar por día"
            value={`${kwhPorDia.toFixed(1)} kWh`}
            sub={`${diasRestantes} ${diasRestantes === 1 ? "día restante" : "días restantes"}`}
          />
        )}
      </div>
    </Card>
  );
}

function Kpi({ label, value, sub, accent }: { label: string; value: string; sub: string; accent?: string }) {
  return (
    <div style={{
      background:   bg.surface,
      borderRadius: `${radius.md}px`,
      padding:      `${space[4]}px ${space[5]}px`,
    }}>
      <p style={{
        margin:        0,
        fontSize:      fontSize.xs,
        fontWeight:    fontWeight.semibold,
        color:         fg.secondary,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
      }}>
        {label}
      </p>
      <p style={{
        margin:     `${space[1]}px 0`,
        fontSize:   fontSize.lg,
        fontWeight: fontWeight.bold,
        color:      accent ?? fg.primary,
        fontFamily: font.technical,
        lineHeight: 1.2,
      }}>
        {value}
      </p>
      <p style={{ margin: 0, fontSize: fontSize.xs, color: fg.muted }}>{sub}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Row 5 — Editor del objetivo
// ---------------------------------------------------------------------------
function EditorObjetivo({
  objetivo, inputKwh, errorMsg, guardando, onChange, onGuardar,
}: {
  objetivo: ObjetivoResponse | null;
  inputKwh: string;
  errorMsg: string | null;
  guardando: boolean;
  onChange: (v: string) => void;
  onGuardar: () => void;
}) {
  return (
    <Card>
      <Label>{objetivo ? "Modificar objetivo" : "Configurar objetivo"}</Label>
      <p style={{ fontSize: fontSize.sm, color: fg.secondary, margin: `${space[2]}px 0 ${space[4]}px` }}>
        Establecé tu meta mensual en kWh para recibir alertas cuando te acercás al límite.
      </p>
      <div style={{ display: "flex", gap: space[3], alignItems: "flex-start", maxWidth: 420 }}>
        <div style={{ flex: 1 }}>
          <input
            type="number"
            min={1}
            step={1}
            value={inputKwh}
            onChange={(e) => onChange(e.target.value)}
            placeholder="ej. 150"
            aria-label="Objetivo en kWh"
            style={{
              width:        "100%",
              padding:      `${space[3]}px ${space[4]}px`,
              border:       `1px solid ${errorMsg ? color.errorDark : border.default}`,
              borderRadius: radius.md,
              fontSize:     fontSize.base,
              fontFamily:   font.technical,
              outline:      "none",
              boxSizing:    "border-box",
              background:   bg.surface,
              color:        fg.primary,
            }}
          />
          {errorMsg && (
            <p style={{ color: color.errorDark, fontSize: fontSize.xs, margin: `${space[1]}px 0 0` }}>
              {errorMsg}
            </p>
          )}
        </div>
        <span style={{ color: fg.muted, fontFamily: font.sans, fontSize: fontSize.sm, paddingTop: space[3] }}>kWh</span>
        <button
          onClick={onGuardar}
          disabled={guardando}
          style={{
            padding:      `${space[3]}px ${space[6]}px`,
            background:   color.green700,
            color:        fg.onDark,
            border:       "none",
            borderRadius: radius.md,
            fontSize:     fontSize.sm,
            fontWeight:   fontWeight.semibold,
            cursor:       guardando ? "wait" : "pointer",
            whiteSpace:   "nowrap",
          }}
        >
          {guardando ? "Guardando…" : "Guardar"}
        </button>
      </div>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Primitivos compartidos
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

function DiasRestantesChip({ dias, sem }: { dias: number; sem: { text: string; chipBg: string } }) {
  return (
    <span style={{
      display:       "inline-flex",
      alignItems:    "baseline",
      gap:           space[1],
      flexShrink:    0,
      padding:       `${space[1]}px ${space[3]}px`,
      borderRadius:  radius.full,
      background:    sem.chipBg,
      color:         sem.text,
      fontFamily:    font.sans,
      fontSize:      fontSize.xs,
      fontWeight:    fontWeight.semibold,
      whiteSpace:    "nowrap",
    }}>
      <span style={{ fontFamily: font.technical, fontSize: fontSize.sm, fontWeight: fontWeight.bold }}>
        {dias}
      </span>
      {dias === 1 ? "día restante" : "días restantes"}
    </span>
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
