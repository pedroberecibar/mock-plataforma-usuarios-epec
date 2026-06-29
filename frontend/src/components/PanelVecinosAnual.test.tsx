import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { PanelVecinosAnual } from "./PanelVecinosAnual";
import type { ComparacionAnual } from "../utils/consumo";

const COMPARACION: ComparacionAnual = {
  meses: [
    { mes: "2026-01", miKwh: 100, zonaKwh: 90, nVecinos: 6 },
    { mes: "2026-02", miKwh: 120, zonaKwh: 110, nVecinos: 7 },
  ],
  totalMioKwh: 220,
  totalZonaKwh: 200,
  diferenciaTotalPct: 10,
  promedioMensualMioKwh: 110,
  promedioMensualZonaKwh: 100,
  diferenciaPromedioPct: 10,
  nVecinos: 7,
  mesesConZona: 2,
};

describe("PanelVecinosAnual", () => {
  it("muestra el año en el título", () => {
    render(<PanelVecinosAnual comparacion={COMPARACION} anio={2026} />);
    expect(screen.getByText(/Comparación con vecinos · 2026/)).not.toBeNull();
  });

  it("muestra los KPIs anuales (total y promedio mensual)", () => {
    render(<PanelVecinosAnual comparacion={COMPARACION} anio={2026} />);
    expect(screen.getByText(/Total del año/)).not.toBeNull();
    expect(screen.getByText(/Promedio mensual/)).not.toBeNull();
    expect(screen.getByText(/vecinos en tu zona/)).not.toBeNull();
  });

  it("muestra estado de carga cuando la comparación es null", () => {
    render(<PanelVecinosAnual comparacion={null} anio={2026} />);
    expect(screen.getByText(/Cargando comparación anual/)).not.toBeNull();
  });

  it("muestra estado vacío cuando no hay meses con zona", () => {
    render(<PanelVecinosAnual comparacion={{ ...COMPARACION, mesesConZona: 0 }} anio={2026} />);
    expect(screen.getByText(/Sin datos de vecinos/)).not.toBeNull();
  });
});
