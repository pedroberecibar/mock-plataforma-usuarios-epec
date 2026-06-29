import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { GraficoConsumoMensual } from "./GraficoConsumoMensual";

describe("GraficoConsumoMensual", () => {
  it("muestra estado vacío cuando la serie está vacía", () => {
    render(<GraficoConsumoMensual serie={[]} />);
    expect(screen.getByText(/Sin datos de consumo/)).not.toBeNull();
  });

  it("no muestra el mensaje vacío cuando hay datos", () => {
    render(<GraficoConsumoMensual serie={[{ mes: "2026-01", kwh: 100 }, { mes: "2026-02", kwh: 120 }]} />);
    expect(screen.queryByText(/Sin datos de consumo/)).toBeNull();
  });
});
