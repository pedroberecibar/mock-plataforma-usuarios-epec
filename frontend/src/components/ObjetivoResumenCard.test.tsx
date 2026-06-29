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
    render(<ObjetivoResumenCard objetivo={OBJETIVO} consumoActualKwh={100} estado={makeEstado()} onEditar={() => {}} />);
    expect(screen.getByText("200")).not.toBeNull();
  });

  it("ya no muestra 'Consumo actual' (vive en el hero de Mi Consumo)", () => {
    render(<ObjetivoResumenCard objetivo={OBJETIVO} consumoActualKwh={196} estado={makeEstado()} onEditar={() => {}} />);
    expect(screen.queryByText(/Consumo actual/i)).toBeNull();
  });

  it("divide el contenido en card de objetivo y card de progreso", () => {
    render(<ObjetivoResumenCard objetivo={OBJETIVO} consumoActualKwh={100} estado={makeEstado()} onEditar={() => {}} />);
    expect(screen.getByText(/Tu objetivo de/i)).not.toBeNull();
    expect(screen.getByText(/Progreso del mes/i)).not.toBeNull();
  });

  it("muestra el faltante cuando el consumo está por debajo del objetivo", () => {
    render(<ObjetivoResumenCard objetivo={OBJETIVO} consumoActualKwh={196} estado={makeEstado()} onEditar={() => {}} />);
    expect(screen.getByText(/Faltante/i)).not.toBeNull();
    // 200 - 196 = 4
    expect(screen.getByText(/^4 kWh$/)).not.toBeNull();
  });

  it("muestra la barra de progreso a todo el ancho cuando hay objetivo y consumo", () => {
    render(<ObjetivoResumenCard objetivo={OBJETIVO} consumoActualKwh={100} estado={makeEstado()} onEditar={() => {}} />);
    const bar = screen.getByRole("progressbar", { name: "Consumo vs objetivo" });
    expect(bar).not.toBeNull();
    expect(bar.style.width).toBe("100%");
  });

  it("mide el consumo en días (como en Objetivos)", () => {
    render(<ObjetivoResumenCard objetivo={OBJETIVO} consumoActualKwh={100} estado={makeEstado()} onEditar={() => {}} />);
    expect(screen.getByText(/Días de consumo/i)).not.toBeNull();
    expect(screen.getByRole("progressbar", { name: "Días objetivo consumidos" })).not.toBeNull();
    expect(screen.getByText(/14.0 de 15 días objetivo consumidos/i)).not.toBeNull();
  });

  it("no muestra barra de progreso cuando no hay objetivo configurado", () => {
    render(
      <ObjetivoResumenCard
        objetivo={null}
        consumoActualKwh={null}
        estado={makeEstado({ objetivo_kwh: null, texto_dinamico: "sin_objetivo" })}
        onEditar={() => {}}
      />
    );
    expect(screen.queryByRole("progressbar")).toBeNull();
  });

  it("ofrece un link 'Editar objetivo' que dispara onEditar al hacer click", () => {
    const onEditar = vi.fn();
    render(<ObjetivoResumenCard objetivo={OBJETIVO} consumoActualKwh={100} estado={makeEstado()} onEditar={onEditar} />);
    fireEvent.click(screen.getByText(/Editar objetivo/i));
    expect(onEditar).toHaveBeenCalledTimes(1);
  });

  it("muestra 'Definir objetivo' y dispara onEditar cuando no hay objetivo", () => {
    const onEditar = vi.fn();
    render(
      <ObjetivoResumenCard
        objetivo={null}
        consumoActualKwh={null}
        estado={makeEstado({ objetivo_kwh: null, texto_dinamico: "sin_objetivo" })}
        onEditar={onEditar}
      />
    );
    fireEvent.click(screen.getByText(/Definir objetivo/i));
    expect(onEditar).toHaveBeenCalledTimes(1);
  });

  it("muestra advertencia de aviso cuando el consumo supera el 80% del objetivo", () => {
    // 170 / 200 = 0.85 → enAviso
    render(
      <ObjetivoResumenCard
        objetivo={OBJETIVO}
        consumoActualKwh={170}
        estado={makeEstado({ texto_dinamico: "sobre_ritmo" })}
        onEditar={() => {}}
      />
    );
    expect(screen.getByRole("alert")).not.toBeNull();
  });

  it("muestra excedente cuando el objetivo está superado", () => {
    render(
      <ObjetivoResumenCard
        objetivo={OBJETIVO}
        consumoActualKwh={250}
        estado={makeEstado({ texto_dinamico: "agotado", excedente_kwh: 50 })}
        onEditar={() => {}}
      />
    );
    expect(screen.getByText(/Excedente/i)).not.toBeNull();
    expect(screen.getByText(/^50 kWh$/)).not.toBeNull();
  });

  it("no usa gradientes en la barra de progreso (tonos planos)", () => {
    render(<ObjetivoResumenCard objetivo={OBJETIVO} consumoActualKwh={100} estado={makeEstado()} onEditar={() => {}} />);
    const bar = screen.getByRole("progressbar", { name: "Consumo vs objetivo" });
    const fill = bar.firstElementChild as HTMLElement;
    expect(fill.style.background).not.toMatch(/gradient/i);
  });
});
