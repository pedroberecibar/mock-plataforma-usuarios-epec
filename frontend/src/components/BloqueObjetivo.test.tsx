import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BloqueObjetivo } from "./BloqueObjetivo";
import type { ObjetivoEstadoResponse } from "../api/types";

const base: ObjetivoEstadoResponse = {
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
};

function estado(over: Partial<ObjetivoEstadoResponse>): ObjetivoEstadoResponse {
  return { ...base, ...over };
}

describe("BloqueObjetivo", () => {
  it("sin estado muestra el CTA para definir objetivo", () => {
    render(<BloqueObjetivo estado={null} />);
    expect(screen.getByRole("button", { name: /definí tu objetivo/i })).not.toBeNull();
  });

  it("con texto_dinamico sin_objetivo muestra el CTA", () => {
    render(
      <BloqueObjetivo
        estado={estado({ texto_dinamico: "sin_objetivo", objetivo_kwh: null })}
      />,
    );
    expect(screen.getByRole("button", { name: /definí tu objetivo/i })).not.toBeNull();
  });

  it("muestra los kWh restantes y la etiqueta del semáforo", () => {
    render(<BloqueObjetivo estado={estado({ objetivo_kwh: 200, consumo_acumulado_kwh: 80 })} />);
    expect(screen.getByText("120")).not.toBeNull();
    expect(screen.getByText(/en línea/i)).not.toBeNull();
  });

  it("con estado agotado avisa que se alcanzó el objetivo", () => {
    render(<BloqueObjetivo estado={estado({ texto_dinamico: "agotado" })} />);
    expect(screen.getByText(/alcanzaste/i)).not.toBeNull();
  });

  it("navega a objetivos al tocar ver detalle", async () => {
    const onNavegar = vi.fn();
    render(<BloqueObjetivo estado={estado({})} onNavegar={onNavegar} />);
    await userEvent.click(screen.getByRole("button", { name: /ver detalle/i }));
    expect(onNavegar).toHaveBeenCalledWith("objetivos");
  });

  it("tiene aria-label de sección", () => {
    render(<BloqueObjetivo estado={estado({})} />);
    expect(screen.getByRole("region", { name: "objetivo del mes" })).not.toBeNull();
  });
});
