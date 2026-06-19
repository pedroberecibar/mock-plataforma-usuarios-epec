import { useEffect, useState } from "react";
import { color, fontSize, fontWeight, radius, space } from "../design-tokens";
import {
  fetchObjetivoSugerido,
  setObjetivo,
  type ObjetivoResponse,
} from "../api/objetivos";
import type { ObjetivoSugeridoResponse } from "../api/types";

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
    fetchObjetivoSugerido(suministroId, mesActualYYYYMM())
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

  return (
    <div style={{ padding: `${space[8]}px ${space[6]}px`, maxWidth: 520, margin: "0 auto" }}>
      <h1 style={{ fontSize: fontSize["2xl"], fontWeight: fontWeight.bold, color: color.neutral900, margin: `0 0 ${space[2]}px` }}>
        ¡Bienvenido!
      </h1>
      <p style={{ fontSize: fontSize.sm, color: color.neutral700, margin: `0 0 ${space[6]}px` }}>
        Fijá tu objetivo de consumo mensual para hacer seguimiento de tu energía.
      </p>

      {cargando && (
        <p style={{ color: color.neutral500, fontSize: fontSize.sm }}>Calculando objetivo sugerido…</p>
      )}

      {!cargando && !modoManual && (
        <div style={{ background: color.white, border: `1px solid ${color.neutral200}`, borderRadius: radius.lg, padding: space[6] }}>
          {sugerido && !sugerido.sin_datos && sugerido.valor_kwh != null ? (
            <>
              <p style={{ fontSize: fontSize.sm, color: color.neutral600, margin: `0 0 ${space[2]}px` }}>
                Objetivo sugerido según tu zona ({sugerido.n_vecinos} vecinos cercanos):
              </p>
              <p style={{ fontSize: "2.5rem", fontWeight: fontWeight.bold, color: color.green700, margin: `0 0 ${space[6]}px` }}>
                {Math.round(sugerido.valor_kwh)} <span style={{ fontSize: fontSize.base, color: color.neutral500 }}>kWh / mes</span>
              </p>
              <div style={{ display: "flex", gap: space[3], flexDirection: "column" }}>
                <button
                  onClick={handleUsarSugerido}
                  disabled={guardando}
                  style={{
                    padding: `${space[3]}px ${space[5]}px`,
                    background: color.green700,
                    color: color.white,
                    border: "none",
                    borderRadius: radius.md,
                    fontSize: fontSize.sm,
                    fontWeight: fontWeight.semibold,
                    cursor: "pointer",
                  }}
                >
                  {guardando ? "Guardando…" : "Usar este objetivo"}
                </button>
                <button
                  onClick={() => setModoManual(true)}
                  style={{
                    padding: `${space[3]}px ${space[5]}px`,
                    background: "transparent",
                    color: color.green700,
                    border: `1px solid ${color.green700}`,
                    borderRadius: radius.md,
                    fontSize: fontSize.sm,
                    fontWeight: fontWeight.medium,
                    cursor: "pointer",
                  }}
                >
                  Ingresar mi objetivo
                </button>
              </div>
            </>
          ) : (
            <>
              <p style={{ fontSize: fontSize.sm, color: color.neutral600, margin: `0 0 ${space[4]}px` }}>
                Sin datos suficientes de tu zona. Podés ingresar tu objetivo manualmente.
              </p>
              <button
                onClick={() => setModoManual(true)}
                style={{
                  padding: `${space[3]}px ${space[5]}px`,
                  background: color.green700,
                  color: color.white,
                  border: "none",
                  borderRadius: radius.md,
                  fontSize: fontSize.sm,
                  fontWeight: fontWeight.semibold,
                  cursor: "pointer",
                }}
              >
                Ingresar mi objetivo
              </button>
            </>
          )}
        </div>
      )}

      {!cargando && modoManual && (
        <div style={{ background: color.white, border: `1px solid ${color.neutral200}`, borderRadius: radius.lg, padding: space[6] }}>
          <p style={{ fontSize: fontSize.sm, color: color.neutral700, margin: `0 0 ${space[4]}px` }}>
            Ingresá tu meta mensual en kWh:
          </p>
          <div style={{ display: "flex", gap: space[3], alignItems: "flex-start", marginBottom: space[4] }}>
            <input
              type="number"
              min={1}
              step={1}
              value={inputKwh}
              onChange={(e) => setInputKwh(e.target.value)}
              placeholder="ej. 150"
              aria-label="Objetivo en kWh"
              style={{
                flex: 1,
                padding: `${space[3]}px ${space[4]}px`,
                border: `1px solid ${errorMsg ? color.errorDark : color.neutral300}`,
                borderRadius: radius.md,
                fontSize: fontSize.base,
                outline: "none",
              }}
            />
            <span style={{ color: color.neutral500, fontSize: fontSize.sm, paddingTop: space[3] }}>kWh</span>
          </div>
          {errorMsg && (
            <p style={{ color: color.errorDark, fontSize: fontSize.xs, margin: `0 0 ${space[3]}px` }}>{errorMsg}</p>
          )}
          <div style={{ display: "flex", gap: space[3] }}>
            <button
              onClick={handleGuardarManual}
              disabled={guardando}
              style={{
                padding: `${space[3]}px ${space[5]}px`,
                background: color.green700,
                color: color.white,
                border: "none",
                borderRadius: radius.md,
                fontSize: fontSize.sm,
                fontWeight: fontWeight.semibold,
                cursor: "pointer",
              }}
            >
              {guardando ? "Guardando…" : "Guardar"}
            </button>
            {sugerido && !sugerido.sin_datos && (
              <button
                onClick={() => setModoManual(false)}
                style={{
                  padding: `${space[3]}px ${space[5]}px`,
                  background: "transparent",
                  color: color.neutral600,
                  border: `1px solid ${color.neutral300}`,
                  borderRadius: radius.md,
                  fontSize: fontSize.sm,
                  cursor: "pointer",
                }}
              >
                Volver
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
