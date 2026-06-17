import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { PanelComparacion } from "./PanelComparacion";
import type { PeriodoConsumo } from "../api/types";

const periodoVacio: PeriodoConsumo = { mes: "2026-06-01", serie: [], total_kwh: null };
const periodoConDatos: PeriodoConsumo = { mes: "2026-06-01", serie: [], total_kwh: 123.4 };

describe("PanelComparacion", () => {
  it('muestra "Sin datos" en los tres períodos cuando no hay datos', () => {
    render(
      <PanelComparacion
        mesActual={periodoVacio}
        mesAnterior={periodoVacio}
        mismoMesAnioAnterior={periodoVacio}
      />,
    );
    const sinDatos = screen.getAllByText("Sin datos");
    expect(sinDatos.length).toBe(3);
  });

  it("muestra el total en kWh cuando hay datos", () => {
    render(
      <PanelComparacion
        mesActual={periodoConDatos}
        mesAnterior={periodoVacio}
        mismoMesAnioAnterior={periodoVacio}
      />,
    );
    expect(screen.getByText("123.4")).not.toBeNull();
    expect(screen.getAllByText("kWh").length).toBeGreaterThan(0);
  });

  it("renderiza las tres tarjetas con sus etiquetas", () => {
    render(
      <PanelComparacion
        mesActual={periodoVacio}
        mesAnterior={periodoVacio}
        mismoMesAnioAnterior={periodoVacio}
      />,
    );
    expect(screen.getByText("Este mes")).not.toBeNull();
    expect(screen.getByText("Mes anterior")).not.toBeNull();
    expect(screen.getByText("Mismo mes año anterior")).not.toBeNull();
  });
});
