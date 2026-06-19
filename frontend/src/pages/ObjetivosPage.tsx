import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { color, fontSize, fontWeight, radius, space } from "../design-tokens";
import {
  evaluarObjetivo,
  fetchObjetivoEstado,
  fetchObjetivo,
  setObjetivo,
  type ObjetivoResponse,
} from "../api/objetivos";
import type { ObjetivoEstadoResponse } from "../api/types";

interface ObjetivosPageProps {
  token: string;
  suministroId: string;
}

type Estado = "cargando" | "sin_objetivo" | "con_objetivo" | "editando" | "guardando" | "error";

function mesActualYYYYMM(): string {
  const now = new Date();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  return `${now.getFullYear()}-${m}`;
}

const WARN_THRESHOLD = 0.8;

export function ObjetivosPage({ token, suministroId }: ObjetivosPageProps) {
  const [objetivo, setObjetivoState] = useState<ObjetivoResponse | null>(null);
  const [estado, setEstado] = useState<Estado>("cargando");
  const [inputKwh, setInputKwh] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [estadoObj, setEstadoObj] = useState<ObjetivoEstadoResponse | null>(null);

  useEffect(() => {
    let cancelled = false;
    const mes = mesActualYYYYMM();

    Promise.all([
      fetchObjetivo(token),
      fetchObjetivoEstado(token, suministroId, mes).catch(() => null),
    ]).then(([obj, est]) => {
      if (cancelled) return;
      setObjetivoState(obj);
      setEstado(obj ? "con_objetivo" : "sin_objetivo");
      if (obj) setInputKwh(String(obj.valor_kwh));
      setEstadoObj(est);
    }).catch(() => {
      if (!cancelled) setEstado("error");
    });

    // Trigger fire-and-forget
    evaluarObjetivo(token);

    return () => { cancelled = true; };
  }, [token, suministroId]);

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
      // Recargar estado de indicadores
      const mes = mesActualYYYYMM();
      const est = await fetchObjetivoEstado(token, suministroId, mes).catch(() => null);
      setEstadoObj(est);
    } catch {
      setEstado("error");
    }
  }

  // Para compatibilidad con tests existentes: cálculo del pct simple
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

  const barColor = superado
    ? color.errorDark
    : enAviso
      ? color.warningDark
      : color.green500;

  return (
    <div style={{ padding: `${space[8]}px ${space[6]}px`, maxWidth: 560, margin: "0 auto" }}>
      <h1 style={{ fontSize: fontSize["2xl"], fontWeight: fontWeight.bold, color: color.neutral900, margin: `0 0 ${space[2]}px` }}>
        Objetivo de consumo
      </h1>
      <p style={{ fontSize: fontSize.sm, color: color.neutral700, margin: `0 0 ${space[8]}px` }}>
        Establecé tu meta mensual en kWh para recibir alertas cuando te acercás al límite.
      </p>

      {estado === "cargando" && (
        <p style={{ color: color.neutral500, fontSize: fontSize.sm }}>Cargando…</p>
      )}

      {estado === "error" && (
        <p style={{ color: color.errorDark, fontSize: fontSize.sm }}>
          Error al cargar el objetivo. Intentá de nuevo.
        </p>
      )}

      {(estado === "con_objetivo" || estado === "sin_objetivo") && (
        <Card>
          {objetivo && (
            <div style={{ marginBottom: space[6] }}>
              <Label>Objetivo vigente</Label>
              <p style={{ fontSize: "2.5rem", fontWeight: fontWeight.bold, color: color.green700, margin: `${space[1]}px 0 0` }}>
                {objetivo.valor_kwh} <span style={{ fontSize: fontSize.base, color: color.neutral500 }}>kWh / mes</span>
              </p>
              <p style={{ fontSize: fontSize.xs, color: color.neutral500, marginTop: space[1] }}>
                Configurado el {new Date(objetivo.vigente_desde).toLocaleDateString("es-AR")}
              </p>
            </div>
          )}

          {/* ── Barra de progreso (compatibilidad tests existentes) ── */}
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
                    background:   superado ? color.errorLight : color.warningLight,
                    color:        superado ? color.errorDark   : color.warningDark,
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
                  background:   color.neutral200,
                  borderRadius: radius.full,
                  overflow:     "hidden",
                }}
              >
                <div style={{
                  height:      "100%",
                  width:       `${Math.round(pct * 100)}%`,
                  background:  barColor,
                  borderRadius: radius.full,
                  transition:  "width 0.3s ease",
                }} />
              </div>

              <p style={{ fontSize: fontSize.xs, color: color.neutral500, marginTop: space[1] }}>
                {Math.round(consumoActual)} de {estadoObj.objetivo_kwh} kWh ({Math.round(pct * 100)}%)
              </p>
            </div>
          )}

          {/* ── Indicador 2: Días objetivo consumidos ── */}
          {estadoObj && estadoObj.texto_dinamico !== "sin_objetivo" && (
            <IndicadorDias estado={estadoObj} />
          )}

          {/* ── Indicador 3: Consumo diario real vs objetivo ── */}
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

          {/* ── Indicador 1: Tu objetivo vs tu zona ── */}
          {estadoObj && estadoObj.promedio_vecinos_kwh != null && estadoObj.diferencia_pct != null && (
            <div style={{ marginBottom: space[6] }}>
              <Label>Tu objetivo vs tu zona</Label>
              <div style={{ marginTop: space[2] }}>
                <span
                  style={{
                    display: "inline-block",
                    padding: `${space[1]}px ${space[3]}px`,
                    borderRadius: radius.full,
                    fontSize: fontSize.sm,
                    fontWeight: fontWeight.semibold,
                    background: estadoObj.diferencia_pct > 0 ? color.errorLight : color.green50,
                    color: estadoObj.diferencia_pct > 0 ? color.errorDark : color.green700,
                  }}
                >
                  {estadoObj.diferencia_pct > 0 ? "+" : ""}
                  {estadoObj.diferencia_pct.toFixed(1)}% vs zona ({estadoObj.n_vecinos} vecinos)
                </span>
                <p style={{ fontSize: fontSize.xs, color: color.neutral500, marginTop: space[1] }}>
                  Promedio zonal: {Math.round(estadoObj.promedio_vecinos_kwh)} kWh/mes
                </p>
              </div>
            </div>
          )}

          {estadoObj && estadoObj.promedio_vecinos_kwh == null && estadoObj.texto_dinamico !== "sin_objetivo" && (
            <p style={{ fontSize: fontSize.xs, color: color.neutral400, marginBottom: space[4] }}>
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
                  border:       `1px solid ${errorMsg ? color.errorDark : color.neutral300}`,
                  borderRadius: radius.md,
                  fontSize:     fontSize.base,
                  outline:      "none",
                  boxSizing:    "border-box",
                }}
              />
              {errorMsg && (
                <p style={{ color: color.errorDark, fontSize: fontSize.xs, margin: `${space[1]}px 0 0` }}>
                  {errorMsg}
                </p>
              )}
            </div>
            <span style={{ color: color.neutral500, fontSize: fontSize.sm, paddingTop: space[3] }}>kWh</span>
            <button
              onClick={handleGuardar}
              style={{
                padding:      `${space[3]}px ${space[5]}px`,
                background:   color.green700,
                color:        color.white,
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
    bajo_ritmo:  { bg: color.green50, text: color.green700 },
    en_ritmo:    { bg: color.green50, text: color.green700 },
    sobre_ritmo: { bg: color.warningLight, text: color.warningDark },
    agotado:     { bg: color.errorLight, text: color.errorDark },
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
              background:   color.neutral200,
              borderRadius: radius.full,
              overflow:     "hidden",
            }}
          >
            <div style={{
              height:      "100%",
              width:       `${Math.round(barPct * 100)}%`,
              background:  c.text,
              borderRadius: radius.full,
              transition:  "width 0.3s ease",
            }} />
          </div>
          <p style={{ fontSize: fontSize.xs, color: color.neutral500, marginTop: space[1] }}>
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
      display:      "flex",
      flexDirection: "column",
      alignItems:   "center",
      padding:      `${space[2]}px ${space[4]}px`,
      border:       `1px solid ${accent}`,
      borderRadius: radius.md,
      minWidth:     80,
    }}>
      <span style={{ fontSize: fontSize.base, fontWeight: fontWeight.bold, color: accent }}>{label}</span>
      <span style={{ fontSize: fontSize.xs, color: color.neutral500 }}>{sublabel}</span>
    </div>
  );
}

function Card({ children }: { children: ReactNode }) {
  return (
    <div style={{
      background:   color.white,
      borderRadius: radius.lg,
      border:       `1px solid ${color.neutral200}`,
      padding:      `${space[6]}px`,
    }}>
      {children}
    </div>
  );
}

function Label({ children }: { children: ReactNode }) {
  return (
    <p style={{ fontSize: fontSize.xs, fontWeight: fontWeight.semibold, color: color.neutral500, textTransform: "uppercase", letterSpacing: "0.07em", margin: 0 }}>
      {children}
    </p>
  );
}
