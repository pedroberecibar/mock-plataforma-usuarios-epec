import { describe, expect, it } from "vitest";
import { resumenObjetivo, semaforoDeObjetivo } from "./objetivo";
import type { ObjetivoEstadoResponse } from "../api/types";

function estado(over: Partial<ObjetivoEstadoResponse>): ObjetivoEstadoResponse {
  return {
    objetivo_kwh: 200,
    promedio_vecinos_kwh: null,
    n_vecinos: 0,
    diferencia_pct: null,
    dias_transcurridos: 10,
    dias_objetivo_consumidos: 8,
    texto_dinamico: "en_ritmo",
    excedente_kwh: null,
    consumo_diario_real_kwh: null,
    consumo_diario_objetivo_kwh: null,
    consumo_acumulado_kwh: 80,
    consumo_promedio_diario_kwh: 8,
    ...over,
  };
}

describe("semaforoDeObjetivo", () => {
  it("en_ritmo y bajo_ritmo mapean a nivel bien", () => {
    expect(semaforoDeObjetivo("en_ritmo").nivel).toBe("bien");
    expect(semaforoDeObjetivo("bajo_ritmo").nivel).toBe("bien");
  });

  it("sobre_ritmo mapea a aviso", () => {
    expect(semaforoDeObjetivo("sobre_ritmo").nivel).toBe("aviso");
  });

  it("agotado mapea a superado", () => {
    expect(semaforoDeObjetivo("agotado").nivel).toBe("superado");
  });

  it("sin_objetivo mapea a sin_objetivo", () => {
    expect(semaforoDeObjetivo("sin_objetivo").nivel).toBe("sin_objetivo");
  });

  it("cada estado tiene una etiqueta legible", () => {
    expect(semaforoDeObjetivo("en_ritmo").label.length).toBeGreaterThan(0);
    expect(semaforoDeObjetivo("agotado").label.length).toBeGreaterThan(0);
  });
});

describe("resumenObjetivo", () => {
  it("calcula kWh restantes, días restantes y kWh por día", () => {
    const r = resumenObjetivo(
      estado({ objetivo_kwh: 200, consumo_acumulado_kwh: 80, dias_transcurridos: 10 }),
      30,
    );
    expect(r.kwhRestantes).toBe(120);
    expect(r.diasRestantes).toBe(20);
    expect(r.kwhPorDia).toBeCloseTo(6, 5);
  });

  it("kWh restantes nunca es negativo cuando el objetivo se superó", () => {
    const r = resumenObjetivo(estado({ objetivo_kwh: 200, consumo_acumulado_kwh: 240 }), 30);
    expect(r.kwhRestantes).toBe(0);
  });

  it("kwhPorDia es null cuando no quedan días en el mes", () => {
    const r = resumenObjetivo(estado({ dias_transcurridos: 30 }), 30);
    expect(r.diasRestantes).toBe(0);
    expect(r.kwhPorDia).toBeNull();
  });

  it("devuelve null si falta el objetivo o el acumulado", () => {
    const r = resumenObjetivo(estado({ objetivo_kwh: null }), 30);
    expect(r.kwhRestantes).toBeNull();
    expect(r.kwhPorDia).toBeNull();
  });
});
