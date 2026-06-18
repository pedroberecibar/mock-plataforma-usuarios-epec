import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { color, fontSize, fontWeight, radius, space } from "../design-tokens";
import { fetchObjetivo, setObjetivo, type ObjetivoResponse } from "../api/objetivos";

interface ObjetivosPageProps {
  token: string;
}

type Estado = "cargando" | "sin_objetivo" | "con_objetivo" | "editando" | "guardando" | "error";

export function ObjetivosPage({ token }: ObjetivosPageProps) {
  const [objetivo, setObjetivoState] = useState<ObjetivoResponse | null>(null);
  const [estado, setEstado] = useState<Estado>("cargando");
  const [inputKwh, setInputKwh] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchObjetivo(token)
      .then((data) => {
        if (cancelled) return;
        setObjetivoState(data);
        setEstado(data ? "con_objetivo" : "sin_objetivo");
        if (data) setInputKwh(String(data.valor_kwh));
      })
      .catch(() => {
        if (!cancelled) setEstado("error");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

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
