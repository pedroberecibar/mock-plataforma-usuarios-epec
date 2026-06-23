import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { bg, border, color, fg, font, fontSize, fontWeight, radius, space } from "../design-tokens";
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

function diasDelMesActual(): number {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
}

const WARN_THRESHOLD = 0.8;

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

  const superado = estadoObj?.texto_dinamico === "agotado";
  const enAviso = pct !== null && pct >= WARN_THRESHOLD && !superado;

  const progressGradient = superado
    ? "linear-gradient(90deg, #b02020 0%, #e05050 100%)"
    : enAviso
      ? "linear-gradient(90deg, #d4850a 0%, #f0a930 100%)"
      : "linear-gradient(90deg, #124e2f 0%, #227d50 100%)";

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <PageHeader title="Objetivo de consumo" />

      <div style={{ maxWidth: 560, margin: "0 auto", padding: `${space[10]}px` }}>
        <p style={{ fontSize: fontSize.sm, color: fg.secondary, fontFamily: font.sans, margin: `0 0 ${space[8]}px` }}>
          Establecé tu meta mensual en kWh para recibir alertas cuando te acercás al límite.
        </p>

        {estado === "cargando" && <LoadingSkeleton variant="card" />}

        {estado === "error" && (
          <div style={{
            display:      "flex",
            alignItems:   "center",
            gap:          space[3],
            padding:      `${space[3]}px ${space[4]}px`,
            background:   color.errorLight,
            border:       `1px solid ${color.error}`,
            borderRadius: radius.sm,
          }}>
            <p style={{ color: color.errorDark, fontSize: fontSize.sm, margin: 0, flex: 1 }}>
              Error al cargar el objetivo.
            </p>
            <button
              onClick={() => { setEstadoObj(null); setObjetivoState(null); setRetryCount((n) => n + 1); }}
              style={{
                padding:      `${space[1]}px ${space[3]}px`,
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

        {(estado === "con_objetivo" || estado === "sin_objetivo") && (
          <Card>
            {objetivo && (
              <div style={{ marginBottom: space[6] }}>
                <Label>Objetivo vigente</Label>
                <p style={{ fontFamily: font.technical, fontSize: "2.5rem", fontWeight: fontWeight.light, color: color.green700, margin: `${space[1]}px 0 0` }}>
                  {objetivo.valor_kwh} <span style={{ fontFamily: font.sans, fontSize: fontSize.base, color: fg.muted }}>kWh / mes</span>
                </p>
                <p style={{ fontSize: fontSize.xs, color: color.neutral500, marginTop: space[1] }}>
                  Configurado el {new Date(objetivo.vigente_desde).toLocaleDateString("es-AR")}
                </p>
              </div>
            )}

            {pct !== null && estadoObj?.objetivo_kwh && consumoActual !== null && objetivo && (
              <div style={{ marginBottom: space[6] }}>
                <Label>Consumo acumulado este mes</Label>

                {(superado || enAviso) && (
                  <p
                    role="alert"
                    style={{
                      marginTop:    space[2],
                      marginBottom: space[2],
                      padding:      `${space[2]}px ${space[3]}px`,
                      borderRadius: radius.sm,
                      fontSize:     fontSize.sm,
                      fontWeight:   fontWeight.medium,
                      background:   superado ? "rgba(192,57,43,0.08)" : "rgba(230,145,10,0.10)",
                      color:        superado ? color.errorDark          : color.warningDark,
                    }}
                  >
                    {superado
                      ? "Objetivo superado — revisá tu consumo."
                      : `Atención: ya consumiste el ${Math.round(pct * 100)}% del objetivo.`}
                  </p>
                )}

                <div
                  role="progressbar"
                  aria-valuenow={Math.round(pct * 100)}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label="Progreso consumo vs objetivo"
                  style={{
                    marginTop:    space[2],
                    height:       10,
                    background:   bg.selected,
                    borderRadius: radius.full,
                    overflow:     "hidden",
                  }}
                >
                  <div style={{
                    height:       "100%",
                    width:        `${Math.round(pct * 100)}%`,
                    background:   progressGradient,
                    borderRadius: radius.full,
                    transition:   "width 600ms cubic-bezier(0.34, 1.56, 0.64, 1)",
                  }} />
                </div>

                <p style={{ fontSize: fontSize.xs, color: fg.muted, marginTop: space[1] }}>
                  {Math.round(consumoActual)} de {estadoObj.objetivo_kwh} kWh ({Math.round(pct * 100)}%)
                </p>
              </div>
            )}

            {estadoObj && estadoObj.texto_dinamico !== "sin_objetivo" && (
              <IndicadorDias estado={estadoObj} />
            )}

            {estadoObj && estadoObj.consumo_diario_real_kwh != null && estadoObj.consumo_diario_objetivo_kwh != null && (
              <div style={{ marginBottom: space[6] }}>
                <Label>Consumo diario real vs objetivo</Label>
                <div style={{ display: "flex", alignItems: "center", gap: space[3], marginTop: space[2] }}>
                  <Chip
                    label={`${estadoObj.consumo_diario_real_kwh.toFixed(1)} kWh`}
                    sublabel="Último día"
                    accent={estadoObj.consumo_diario_real_kwh <= estadoObj.consumo_diario_objetivo_kwh ? color.green700 : color.errorDark}
                  />
                  <span style={{ color: color.neutral400, fontSize: fontSize.sm }}>vs</span>
                  <Chip
                    label={`${estadoObj.consumo_diario_objetivo_kwh.toFixed(1)} kWh`}
                    sublabel="Objetivo diario"
                    accent={color.neutral600}
                  />
                </div>
              </div>
            )}

            {estadoObj && estadoObj.consumo_acumulado_kwh != null && objetivo && (
              <IndicadoresAdicionales estadoObj={estadoObj} objetivo={objetivo} />
            )}

            {estadoObj && estadoObj.promedio_vecinos_kwh != null && estadoObj.diferencia_pct != null && (
              <div style={{ marginBottom: space[6] }}>
                <Label>Tu objetivo vs tu zona</Label>
                <div style={{ marginTop: space[2] }}>
                  <span
                    style={{
                      display:      "inline-block",
                      padding:      `${space[1]}px ${space[3]}px`,
                      borderRadius: radius.full,
                      fontSize:     fontSize.sm,
                      fontWeight:   fontWeight.semibold,
                      background:   estadoObj.diferencia_pct > 0 ? "rgba(192,57,43,0.08)" : "rgba(18,78,47,0.10)",
                      color:        estadoObj.diferencia_pct > 0 ? color.errorDark : color.green700,
                    }}
                  >
                    {estadoObj.diferencia_pct > 0 ? "+" : ""}
                    {estadoObj.diferencia_pct.toFixed(1)}% vs zona ({estadoObj.n_vecinos} vecinos)
                  </span>
                  <p style={{ fontSize: fontSize.xs, color: fg.muted, marginTop: space[1] }}>
                    Promedio zonal: {Math.round(estadoObj.promedio_vecinos_kwh)} kWh/mes
                  </p>
                </div>
              </div>
            )}

            {estadoObj && estadoObj.promedio_vecinos_kwh == null && estadoObj.texto_dinamico !== "sin_objetivo" && (
              <p style={{ fontSize: fontSize.xs, color: fg.muted, marginBottom: space[4] }}>
                Sin datos suficientes de tu zona
              </p>
            )}

            <Label>{objetivo ? "Modificar objetivo" : "Configurar objetivo"}</Label>
            <div style={{ display: "flex", gap: space[3], marginTop: space[2], alignItems: "flex-start" }}>
              <div style={{ flex: 1 }}>
                <input
                  type="number"
                  min={1}
                  step={1}
                  value={inputKwh}
                  onChange={(e) => setInputKwh(e.target.value)}
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
                onClick={handleGuardar}
                style={{
                  padding:      `${space[3]}px ${space[5]}px`,
                  background:   color.green700,
                  color:        fg.onDark,
                  border:       "none",
                  borderRadius: radius.md,
                  fontSize:     fontSize.sm,
                  fontWeight:   fontWeight.semibold,
                  cursor:       "pointer",
                  whiteSpace:   "nowrap",
                }}
              >
                Guardar
              </button>
            </div>
          </Card>
        )}

        {estado === "guardando" && (
          <p style={{ color: color.neutral500, fontSize: fontSize.sm }}>Guardando…</p>
        )}
      </div>
    </div>
  );
}

function IndicadorDias({ estado }: { estado: ObjetivoEstadoResponse }) {
  const { texto_dinamico, dias_objetivo_consumidos, dias_transcurridos, excedente_kwh } = estado;

  const mensajes: Record<string, string> = {
    bajo_ritmo: "Vas bien, estás por debajo de tu ritmo objetivo.",
    en_ritmo: "Vas en línea con tu objetivo.",
    sobre_ritmo: "Atención, estás consumiendo más rápido que tu objetivo.",
    agotado: "Ya alcanzaste tu objetivo de consumo de este mes.",
  };

  const colores: Record<string, { bg: string; text: string }> = {
    bajo_ritmo:  { bg: "rgba(18,78,47,0.10)",   text: color.green700 },
    en_ritmo:    { bg: "rgba(18,78,47,0.10)",   text: color.green700 },
    sobre_ritmo: { bg: "rgba(230,145,10,0.10)", text: color.warningDark },
    agotado:     { bg: "rgba(192,57,43,0.08)",  text: color.errorDark },
  };

  const c = colores[texto_dinamico] ?? { bg: color.neutral100, text: color.neutral700 };
  const barPct = dias_objetivo_consumidos != null
    ? Math.min(dias_objetivo_consumidos / dias_transcurridos, 1)
    : 0;

  return (
    <div style={{ marginBottom: space[6] }}>
      <Label>Días de consumo</Label>
      <p
        data-testid="indicador-2-texto"
        style={{
          marginTop:    space[2],
          padding:      `${space[2]}px ${space[3]}px`,
          borderRadius: radius.sm,
          fontSize:     fontSize.sm,
          fontWeight:   fontWeight.medium,
          background:   c.bg,
          color:        c.text,
        }}
      >
        {mensajes[texto_dinamico]}
        {texto_dinamico === "agotado" && excedente_kwh != null && (
          <> Excedente: {excedente_kwh.toFixed(1)} kWh.</>
        )}
      </p>

      {dias_objetivo_consumidos != null && (
        <>
          <div
            style={{
              marginTop:    space[2],
              height:       8,
              background:   bg.selected,
              borderRadius: radius.full,
              overflow:     "hidden",
            }}
          >
            <div style={{
              height:       "100%",
              width:        `${Math.round(barPct * 100)}%`,
              background:   c.text,
              borderRadius: radius.full,
              transition:   "width 600ms cubic-bezier(0.34, 1.56, 0.64, 1)",
            }} />
          </div>
          <p style={{ fontSize: fontSize.xs, color: fg.muted, marginTop: space[1] }}>
            {dias_objetivo_consumidos.toFixed(1)} de {dias_transcurridos} días objetivo consumidos
          </p>
        </>
      )}

      {(texto_dinamico === "sobre_ritmo" || texto_dinamico === "agotado") && (
        <p style={{ fontSize: fontSize.xs, color: color.neutral600, marginTop: space[2] }}>
          💡 Palanca: revisá tus electrodomésticos de mayor consumo o postponé el uso de lavarropas/lavavajillas a horarios de menor demanda.
        </p>
      )}
    </div>
  );
}

function Chip({
  label,
  sublabel,
  accent,
}: {
  label: string;
  sublabel: string;
  accent: string;
}) {
  return (
    <div style={{
      display:       "flex",
      flexDirection: "column",
      alignItems:    "center",
      padding:       `${space[2]}px ${space[4]}px`,
      border:        `1px solid ${accent}`,
      borderRadius:  radius.md,
      minWidth:      80,
    }}>
      <span style={{ fontSize: fontSize.base, fontWeight: fontWeight.bold, color: accent }}>{label}</span>
      <span style={{ fontSize: fontSize.xs, color: fg.muted }}>{sublabel}</span>
    </div>
  );
}

function IndicadoresAdicionales({
  estadoObj,
  objetivo,
}: {
  estadoObj: ObjetivoEstadoResponse;
  objetivo: ObjetivoResponse;
}) {
  const diasDelMes = diasDelMesActual();
  const diasRestantes = Math.max(0, diasDelMes - estadoObj.dias_transcurridos);
  const acumulado = estadoObj.consumo_acumulado_kwh ?? 0;
  const kwh_restantes = Math.max(0, objetivo.valor_kwh - acumulado);
  const kwh_por_dia = diasRestantes > 0 ? kwh_restantes / diasRestantes : null;

  return (
    <div style={{ marginBottom: space[6] }}>
      <Label>Resumen del mes</Label>
      <div
        style={{
          display:             "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
          gap:                 space[3],
          marginTop:           space[3],
        }}
      >
        {estadoObj.consumo_promedio_diario_kwh != null && (
          <MiniKpi
            label="Promedio diario"
            value={`${estadoObj.consumo_promedio_diario_kwh.toFixed(1)} kWh`}
            sub="este mes"
          />
        )}
        <MiniKpi
          label="kWh restantes"
          value={`${kwh_restantes.toFixed(0)} kWh`}
          sub="para cumplir el objetivo"
          accent={kwh_restantes <= 0 ? color.errorDark : color.green700}
        />
        {kwh_por_dia !== null && kwh_restantes > 0 && (
          <MiniKpi
            label="Podés usar por día"
            value={`${kwh_por_dia.toFixed(1)} kWh`}
            sub={`${diasRestantes} días restantes`}
          />
        )}
      </div>
    </div>
  );
}

function MiniKpi({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub: string;
  accent?: string;
}) {
  return (
    <div
      style={{
        background:   bg.page,
        borderRadius: radius.md,
        padding:      `${space[3]}px ${space[4]}px`,
      }}
    >
      <p style={{ margin: 0, fontSize: fontSize.xs, fontWeight: fontWeight.semibold, color: fg.muted, textTransform: "uppercase", letterSpacing: "0.06em" }}>
        {label}
      </p>
      <p style={{ margin: `${space[1]}px 0 ${space[1]}px`, fontSize: fontSize.lg, fontWeight: fontWeight.bold, color: accent ?? fg.primary, fontFamily: font.technical }}>
        {value}
      </p>
      <p style={{ margin: 0, fontSize: fontSize.xs, color: fg.muted }}>{sub}</p>
    </div>
  );
}

function Card({ children }: { children: ReactNode }) {
  return (
    <div style={{
      background:   bg.surface,
      borderRadius: `${radius.lg}px`,
      border:       "none",
      boxShadow:    "0 1px 4px rgba(100,80,60,0.08), 0 1px 2px rgba(100,80,60,0.05)",
      padding:      `${space[8]}px`,
      fontFamily:   font.sans,
    }}>
      {children}
    </div>
  );
}

function Label({ children }: { children: ReactNode }) {
  return (
    <p style={{ fontFamily: font.sans, fontSize: fontSize.xs, fontWeight: fontWeight.semibold, color: fg.muted, textTransform: "uppercase", letterSpacing: "0.07em", margin: 0 }}>
      {children}
    </p>
  );
}
