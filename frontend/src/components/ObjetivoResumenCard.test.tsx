import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ObjetivoResumenCard } from "./ObjetivoResumenCard";
import type { ObjetivoResponse } from "../api/objetivos";
import type { ObjetivoEstadoResponse } from "../api/types";

const OBJETIVO: ObjetivoResponse = {
  valor_kwh: 200,
  origen: "manual",
  vigente_desde: "2026-06-01",
};

function makeEstado(overrides: Partial<ObjetivoEstadoResponse> = {}): ObjetivoEstadoResponse {
  return {
    objetivo_kwh: 200,
    promedio_vecinos_kwh: null,
    n_vecinos: 0,
    diferencia_pct: null,
    dias_transcurridos: 15,
    dias_objetivo_consumidos: 14,
    texto_dinamico: "en_ritmo",
    excedente_kwh: null,
    consumo_diario_real_kwh: 7,
    consumo_diario_objetivo_kwh: 6.67,
    consumo_acumulado_kwh: 100,
    consumo_promedio_diario_kwh: 6.67,
    ...overrides,
  };
}

describe("ObjetivoResumenCard", () => {
  it("muestra el valor del objetivo vigente como número hero", () => {
    render(<ObjetivoResumenCard objetivo={OBJETIVO} estado={makeEstado()} onEditar={() => {}} />);
    expect(screen.getByText("200")).not.toBeNull();
  });

  it("muestra la barra de progreso cuando hay objetivo y consumo", () => {
    render(<ObjetivoResumenCard objetivo={OBJETIVO} estado={makeEstado()} onEditar={() => {}} />);
    expect(screen.getByRole("progressbar")).not.toBeNull();
  });

  it("no muestra barra de progreso cuando no hay objetivo configurado", () => {
    render(
      <ObjetivoResumenCard
        objetivo={null}
        estado={makeEstado({ objetivo_kwh: null, texto_dinamico: "sin_objetivo" })}
        onEditar={() => {}}
      />
    );
    expect(screen.queryByRole("progressbar")).toBeNull();
  });

  it("ofrece un link 'Editar objetivo' que dispara onEditar al hacer click", () => {
    const onEditar = vi.fn();
    render(<ObjetivoResumenCard objetivo={OBJETIVO} estado={makeEstado()} onEditar={onEditar} />);
    fireEvent.click(screen.getByText(/Editar objetivo/i));
    expect(onEditar).toHaveBeenCalledTimes(1);
  });

  it("muestra 'Definir objetivo' y dispara onEditar cuando no hay objetivo", () => {
    const onEditar = vi.fn();
    render(
      <ObjetivoResumenCard
        objetivo={null}
        estado={makeEstado({ objetivo_kwh: null, texto_dinamico: "sin_objetivo" })}
        onEditar={onEditar}
      />
    );
    fireEvent.click(screen.getByText(/Definir objetivo/i));
    expect(onEditar).toHaveBeenCalledTimes(1);
  });

  it("muestra advertencia de aviso cuando el consumo supera el 80% del objetivo", () => {
    // consumoActual = 25 × 6.67 ≈ 166.7 → pct ≈ 0.83 → enAviso
    render(
      <ObjetivoResumenCard
        objetivo={OBJETIVO}
        estado={makeEstado({ dias_objetivo_consumidos: 25, texto_dinamico: "sobre_ritmo" })}
        onEditar={() => {}}
      />
    );
    expect(screen.getByRole("alert")).not.toBeNull();
  });

  it("muestra excedente y estado superado cuando el objetivo está agotado", () => {
    render(
      <ObjetivoResumenCard
        objetivo={OBJETIVO}
        estado={makeEstado({
          texto_dinamico: "agotado",
          excedente_kwh: 50,
          dias_objetivo_consumidos: 30,
          consumo_acumulado_kwh: 250,
        })}
        onEditar={() => {}}
      />
    );
    expect(screen.getByText(/Excedente/i)).not.toBeNull();
    expect(screen.getByText(/50/)).not.toBeNull();
  });

  it("muestra la diferencia vs zona cuando hay datos de vecinos", () => {
    render(
      <ObjetivoResumenCard
        objetivo={OBJETIVO}
        estado={makeEstado({ promedio_vecinos_kwh: 160, diferencia_pct: 25.0, n_vecinos: 6 })}
        onEditar={() => {}}
      />
    );
    expect(screen.getByText(/\+25/)).not.toBeNull();
  });

  it("muestra 'Sin datos' de zona cuando no hay vecinos", () => {
    render(
      <ObjetivoResumenCard
        objetivo={OBJETIVO}
        estado={makeEstado({ promedio_vecinos_kwh: null, diferencia_pct: null, n_vecinos: 0 })}
        onEditar={() => {}}
      />
    );
    expect(screen.getByText(/Sin datos/i)).not.toBeNull();
  });

  it("no usa gradientes en la barra de progreso (tonos planos)", () => {
    render(<ObjetivoResumenCard objetivo={OBJETIVO} estado={makeEstado()} onEditar={() => {}} />);
    const bar = screen.getByRole("progressbar");
    const fill = bar.firstElementChild as HTMLElement;
    expect(fill.style.background).not.toMatch(/gradient/i);
  });
});
