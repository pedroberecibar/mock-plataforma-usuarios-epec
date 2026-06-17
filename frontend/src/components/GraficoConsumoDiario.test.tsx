import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { GraficoConsumoDiario } from "./GraficoConsumoDiario";

describe("GraficoConsumoDiario", () => {
  it("muestra estado vacío cuando la serie está vacía", () => {
    render(<GraficoConsumoDiario serie={[]} />);
    expect(screen.getByText(/Sin datos de consumo/)).not.toBeNull();
  });

  it("no muestra el mensaje vacío cuando hay datos", () => {
    const serie = [
      { fecha: "2026-06-01", kwh: 10 },
      { fecha: "2026-06-02", kwh: 15 },
    ];
    render(<GraficoConsumoDiario serie={serie} />);
    expect(screen.queryByText(/Sin datos de consumo/)).toBeNull();
  });
});
