import { useEffect, useState } from "react";
import {
  bg, border, color, fg, font, fontSize, fontWeight, radius, space,
  cardFeaturedStyle,
} from "../design-tokens";
import {
  fetchObjetivoSugerido,
  setObjetivo,
  type ObjetivoResponse,
} from "../api/objetivos";
import type { ObjetivoSugeridoResponse } from "../api/types";
import { KwhHero } from "../components/KwhHero";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { EmptyState } from "../components/EmptyState";

interface Props {
  token: string;
  suministroId: string;
  onObjetivoGuardado: (objetivo: ObjetivoResponse) => void;
}

function mesActualYYYYMM(): string {
  const now = new Date();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  return `${now.getFullYear()}-${m}`;
}

export function OnboardingObjetivoPage({ token, suministroId, onObjetivoGuardado }: Props) {
  const [sugerido, setSugerido] = useState<ObjetivoSugeridoResponse | null>(null);
  const [cargando, setCargando] = useState(true);
  const [modoManual, setModoManual] = useState(false);
  const [inputKwh, setInputKwh] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchObjetivoSugerido(token, mesActualYYYYMM())
      .then((s) => { if (!cancelled) { setSugerido(s); setCargando(false); } })
      .catch(() => { if (!cancelled) setCargando(false); });
    return () => { cancelled = true; };
  }, [suministroId]);

  async function guardar(kwh: number) {
    setGuardando(true);
    setErrorMsg(null);
    try {
      const nuevo = await setObjetivo(token, kwh);
      onObjetivoGuardado(nuevo);
    } catch {
      setErrorMsg("Error al guardar. Intentá de nuevo.");
      setGuardando(false);
    }
  }

  async function handleUsarSugerido() {
    if (!sugerido?.valor_kwh) return;
    await guardar(sugerido.valor_kwh);
  }

  async function handleGuardarManual() {
    const valor = parseFloat(inputKwh);
    if (isNaN(valor) || valor <= 0) {
      setErrorMsg("Ingresá un valor mayor a 0 kWh");
      return;
    }
    await guardar(valor);
  }

  const tieneSugerido = sugerido && !sugerido.sin_datos && sugerido.valor_kwh != null;

  return (
    <div style={{
      minHeight:      "100vh",
      background:     bg.page,
      fontFamily:     font.sans,
      display:        "flex",
      alignItems:     "center",
      justifyContent: "center",
      padding:        `${space[6]}px ${space[4]}px`,
    }}>
      <div style={{ width: "100%", maxWidth: 480 }}>

        <header style={{ marginBottom: space[8] }}>
          <h1 style={{
            fontFamily:   font.sans,
            fontSize:     fontSize["2xl"],
            fontWeight:   fontWeight.semibold,
            color:        fg.primary,
            margin:       0,
            letterSpacing: "-0.01em",
          }}>
            Bienvenido a EPEC Clientes
          </h1>
          <p style={{
            fontFamily: font.sans,
            fontSize:   fontSize.base,
            color:      fg.secondary,
            margin:     `${space[2]}px 0 0`,
            lineHeight: 1.5,
          }}>
            Establecé tu objetivo de consumo mensual para hacer seguimiento de tu energía.
          </p>
        </header>

        {cargando && <LoadingSkeleton variant="card" />}

        {!cargando && !modoManual && tieneSugerido && (
          <div style={{ ...cardFeaturedStyle }}>
            <p style={{
              fontFamily:  font.sans,
              fontSize:    fontSize.xs,
              fontWeight:  fontWeight.semibold,
              color:       fg.muted,
              textTransform: "uppercase" as const,
              letterSpacing: "0.07em",
              margin:      `0 0 ${space[3]}px`,
            }}>
              Objetivo sugerido para tu zona
            </p>

            <div style={{ marginBottom: space[2] }}>
              <KwhHero
                value={Math.round(sugerido!.valor_kwh!)}
                sublabel={`Basado en ${sugerido!.n_vecinos} vecinos cercanos, mismo mes del año anterior`}
                variant="hero"
                color={color.green700}
              />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: space[3], marginTop: space[8] }}>
              <button
                onClick={handleUsarSugerido}
                disabled={guardando}
                style={{
                  width:        "100%",
                  padding:      `${space[4]}px`,
                  background:   guardando ? color.green400 : color.green700,
                  color:        "#ffffff",
                  border:       "none",
                  borderRadius: radius.md,
                  fontSize:     fontSize.base,
                  fontWeight:   fontWeight.semibold,
                  fontFamily:   font.sans,
                  cursor:       guardando ? "not-allowed" : "pointer",
                  transition:   "background 150ms ease",
                }}
              >
                {guardando ? "Guardando…" : "Usar este objetivo"}
              </button>
              <button
                onClick={() => setModoManual(true)}
                style={{
                  width:        "100%",
                  padding:      `${space[3]}px`,
                  background:   "transparent",
                  color:        color.green700,
                  border:       `1px solid ${color.green700}`,
                  borderRadius: radius.md,
                  fontSize:     fontSize.sm,
                  fontWeight:   fontWeight.medium,
                  fontFamily:   font.sans,
                  cursor:       "pointer",
                  transition:   "background 150ms ease",
                }}
              >
                Ingresar mi objetivo
              </button>
            </div>
          </div>
        )}

        {!cargando && !modoManual && !tieneSugerido && (
          <div style={{ marginBottom: space[6] }}>
            <EmptyState
              title="Sin datos suficientes de tu zona"
              description="Podés ingresar tu objetivo manualmente. Lo podés ajustar en cualquier momento desde la sección Objetivos."
              ctaLabel="Ingresar mi objetivo"
              onCta={() => setModoManual(true)}
            />
          </div>
        )}

        {!cargando && modoManual && (
          <div style={{
            background:   bg.surface,
            borderRadius: radius.lg,
            padding:      `${space[8]}px`,
            boxShadow:    "0 1px 4px rgba(100,80,60,0.08)",
          }}>
            <p style={{
              fontFamily: font.sans,
              fontSize:   fontSize.sm,
              color:      fg.secondary,
              margin:     `0 0 ${space[5]}px`,
              lineHeight: 1.5,
            }}>
              Ingresá tu meta mensual en kWh:
            </p>
            <div style={{ display: "flex", gap: space[3], alignItems: "flex-start", marginBottom: space[4] }}>
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
                    display:      "block",
                    width:        "100%",
                    boxSizing:    "border-box" as const,
                    padding:      `${space[3]}px ${space[4]}px`,
                    border:       `1px solid ${errorMsg ? color.errorDark : border.default}`,
                    borderRadius: radius.md,
                    fontSize:     fontSize.base,
                    fontFamily:   font.technical,
                    color:        fg.primary,
                    background:   bg.surface,
                    outline:      "none",
                    transition:   "border-color 150ms ease",
                  }}
                />
                {errorMsg && (
                  <p style={{ color: color.errorDark, fontSize: fontSize.xs, margin: `${space[1]}px 0 0` }}>
                    {errorMsg}
                  </p>
                )}
              </div>
              <span style={{
                color:      fg.muted,
                fontFamily: font.sans,
                fontSize:   fontSize.sm,
                paddingTop: `${space[3]}px`,
              }}>
                kWh
              </span>
            </div>
            <div style={{ display: "flex", gap: space[3] }}>
              <button
                onClick={handleGuardarManual}
                disabled={guardando}
                style={{
                  flex:         1,
                  padding:      `${space[3]}px`,
                  background:   guardando ? color.green400 : color.green700,
                  color:        "#ffffff",
                  border:       "none",
                  borderRadius: radius.md,
                  fontSize:     fontSize.sm,
                  fontWeight:   fontWeight.semibold,
                  fontFamily:   font.sans,
                  cursor:       guardando ? "not-allowed" : "pointer",
                }}
              >
                {guardando ? "Guardando…" : "Guardar"}
              </button>
              {tieneSugerido && (
                <button
                  onClick={() => setModoManual(false)}
                  style={{
                    padding:      `${space[3]}px ${space[4]}px`,
                    background:   "transparent",
                    color:        fg.secondary,
                    border:       `1px solid ${border.default}`,
                    borderRadius: radius.md,
                    fontSize:     fontSize.sm,
                    fontFamily:   font.sans,
                    cursor:       "pointer",
                  }}
                >
                  Volver
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
