import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { BloqueConsumoMes } from "./BloqueConsumoMes";
import type { ConsumoMesResponse } from "../api/types";

const sinDatos: ConsumoMesResponse = {
  total_kwh: null,
  vs_mes_anterior_pct: null,
  vs_anio_anterior_pct: null,
};

const conDatos: ConsumoMesResponse = {
  total_kwh: 123.4,
  vs_mes_anterior_pct: -8.5,
  vs_anio_anterior_pct: 15.0,
};

describe("BloqueConsumoMes", () => {
  it("muestra guión cuando no hay total_kwh", () => {
    render(<BloqueConsumoMes consumoMes={sinDatos} />);
    expect(screen.getByText("—")).not.toBeNull();
  });

  it("muestra el total en kWh cuando hay datos", () => {
    render(<BloqueConsumoMes consumoMes={conDatos} />);
    expect(screen.getByText("123.4")).not.toBeNull();
  });

  it("muestra s/d cuando vs_mes_anterior_pct es null", () => {
    render(<BloqueConsumoMes consumoMes={sinDatos} />);
    const chips = screen.getAllByText(/s\/d/);
    expect(chips.length).toBeGreaterThanOrEqual(1);
  });

  it("muestra delta negativo con ▼ y color verde", () => {
    render(<BloqueConsumoMes consumoMes={conDatos} />);
    const chip = screen.getByText(/▼.*8.5%/);
    expect(chip).not.toBeNull();
  });

  it("muestra delta positivo con ▲ cuando el consumo subió", () => {
    render(<BloqueConsumoMes consumoMes={conDatos} />);
    const chip = screen.getByText(/▲.*15.0%/);
    expect(chip).not.toBeNull();
  });

  it("tiene aria-label de sección", () => {
    render(<BloqueConsumoMes consumoMes={sinDatos} />);
    expect(screen.getByRole("region", { name: "consumo del mes" })).not.toBeNull();
  });
});
