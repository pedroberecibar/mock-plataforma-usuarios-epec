import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { PanelVecinosComparacion } from "./PanelVecinosComparacion";
import type { ComparacionZonaResponse, PeriodoConsumo } from "../api/types";

const mesActual: PeriodoConsumo = { mes: "2026-06-01", serie: [], total_kwh: 271 };
const mismoMesAnioAnterior: PeriodoConsumo = { mes: "2025-06-01", serie: [], total_kwh: 225 };

describe("PanelVecinosComparacion", () => {
  it("no crashea y muestra estado vacío cuando zona es null", () => {
    render(
      <PanelVecinosComparacion zona={null} mesActual={mesActual} mismoMesAnioAnterior={mismoMesAnioAnterior} />,
    );
    expect(screen.getByText(/Sin datos de vecinos/i)).not.toBeNull();
  });

  it("no crashea cuando zona viene undefined (fixture demo sin zona_mes_actual)", () => {
    // El campo puede faltar en datos mock → llega como undefined, no null.
    render(
      <PanelVecinosComparacion
        zona={undefined as unknown as ComparacionZonaResponse | null}
        mesActual={mesActual}
        mismoMesAnioAnterior={mismoMesAnioAnterior}
      />,
    );
    expect(screen.getByText(/Sin datos de vecinos/i)).not.toBeNull();
  });

  it("muestra las dimensiones cuando hay zona con suficientes vecinos", () => {
    const zona: ComparacionZonaResponse = {
      promedio_vecinos_kwh: 240,
      n_vecinos: 6,
      diferencia_pct: 12.5,
      serie: [],
    };
    render(
      <PanelVecinosComparacion zona={zona} mesActual={mesActual} mismoMesAnioAnterior={mismoMesAnioAnterior} />,
    );
    expect(screen.getByText(/vecinos en tu zona/i)).not.toBeNull();
  });
});
