import type { ObjetivoEstadoResponse, TextoDinamico } from "../api/types";

// Semáforo del objetivo derivado del texto_dinamico que ya calcula el backend
// (sensible al tiempo: 98% faltando 1 día va "en línea", faltando 10 días va rojo).
export type NivelObjetivo = "bien" | "aviso" | "superado" | "sin_objetivo";

export interface SemaforoObjetivo {
  nivel: NivelObjetivo;
  label: string;
}

const SEMAFORO: Record<TextoDinamico, SemaforoObjetivo> = {
  bajo_ritmo:   { nivel: "bien",         label: "Vas bien, por debajo de tu ritmo" },
  en_ritmo:     { nivel: "bien",         label: "Vas en línea con tu objetivo" },
  sobre_ritmo:  { nivel: "aviso",        label: "Vas acelerado para tu objetivo" },
  agotado:      { nivel: "superado",     label: "Alcanzaste tu objetivo del mes" },
  sin_objetivo: { nivel: "sin_objetivo", label: "Sin objetivo definido" },
};

export function semaforoDeObjetivo(texto: TextoDinamico): SemaforoObjetivo {
  return SEMAFORO[texto] ?? SEMAFORO.sin_objetivo;
}

export interface ResumenObjetivo {
  kwhRestantes: number | null;
  kwhPorDia: number | null;
  diasRestantes: number;
}

// kWh que faltan para el objetivo y cuánto se puede usar por día restante.
export function resumenObjetivo(
  estado: ObjetivoEstadoResponse,
  diasDelMes: number,
): ResumenObjetivo {
  const diasRestantes = Math.max(0, diasDelMes - estado.dias_transcurridos);

  if (estado.objetivo_kwh == null || estado.consumo_acumulado_kwh == null) {
    return { kwhRestantes: null, kwhPorDia: null, diasRestantes };
  }

  const kwhRestantes = Math.max(0, estado.objetivo_kwh - estado.consumo_acumulado_kwh);
  const kwhPorDia = diasRestantes > 0 ? kwhRestantes / diasRestantes : null;

  return { kwhRestantes, kwhPorDia, diasRestantes };
}
