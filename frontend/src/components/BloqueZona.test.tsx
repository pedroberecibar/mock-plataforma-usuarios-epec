import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { BloqueZona } from "./BloqueZona";
import type { ComparacionZonaResponse } from "../api/types";

const sinVecinos: ComparacionZonaResponse = {
  promedio_vecinos_kwh: null,
  n_vecinos: 0,
  diferencia_pct: null,
};

const conVecinosMasAlto: ComparacionZonaResponse = {
  promedio_vecinos_kwh: 100.0,
  n_vecinos: 3,
  diferencia_pct: 25.5,
};

const conVecinosMasBajo: ComparacionZonaResponse = {
  promedio_vecinos_kwh: 100.0,
  n_vecinos: 2,
  diferencia_pct: -15.0,
};

describe("BloqueZona", () => {
  it("muestra mensaje sin datos cuando n_vecinos es 0", () => {
    render(<BloqueZona zona={sinVecinos} />);
    expect(screen.getByText("Sin datos de zona disponibles")).not.toBeNull();
  });

  it("muestra porcentaje positivo y texto por encima", () => {
    render(<BloqueZona zona={conVecinosMasAlto} />);
    expect(screen.getByText(/25.5%/)).not.toBeNull();
    expect(screen.getByText(/por encima/)).not.toBeNull();
  });

  it("muestra porcentaje negativo y texto por debajo", () => {
    render(<BloqueZona zona={conVecinosMasBajo} />);
    expect(screen.getByText(/-15.0%/)).not.toBeNull();
    expect(screen.getByText(/por debajo/)).not.toBeNull();
  });

  it("muestra el número de vecinos", () => {
    render(<BloqueZona zona={conVecinosMasAlto} />);
    expect(screen.getByText(/3 vecinos/)).not.toBeNull();
  });

  it("muestra el promedio zonal", () => {
    render(<BloqueZona zona={conVecinosMasAlto} />);
    expect(screen.getByText(/100.0 kWh/)).not.toBeNull();
  });

  it("tiene aria-label de sección", () => {
    render(<BloqueZona zona={sinVecinos} />);
    expect(screen.getByRole("region", { name: "comparación de zona" })).not.toBeNull();
  });
});
