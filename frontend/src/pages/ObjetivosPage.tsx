import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { color, fontSize, fontWeight, radius, space } from "../design-tokens";
import { fetchObjetivo, setObjetivo, type ObjetivoResponse } from "../api/objetivos";
import { fetchHome } from "../api/home";

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
  const [consumoActual, setConsumoActual] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    const mes = mesActualYYYYMM();

    Promise.all([
      fetchObjetivo(token),
      fetchHome(token, suministroId, mes).catch(() => null),
    ]).then(([obj, home]) => {
      if (cancelled) return;
      setObjetivoState(obj);
      setEstado(obj ? "con_objetivo" : "sin_objetivo");
      if (obj) setInputKwh(String(obj.valor_kwh));
      setConsumoActual(home?.consumo_mes.total_kwh ?? null);
    }).catch(() => {
      if (!cancelled) setEstado("error");
    });

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
    } catch {
      setEstado("error");
    }
  }

  const pct = objetivo && consumoActual !== null
    ? Math.min(consumoActual / objetivo.valor_kwh, 1)
    : null;

  const superado = pct !== null && pct >= 1;
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

          {pct !== null && consumoActual !== null && objetivo && (
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
                {consumoActual} de {objetivo.valor_kwh} kWh ({Math.round(pct * 100)}%)
              </p>
            </div>
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
