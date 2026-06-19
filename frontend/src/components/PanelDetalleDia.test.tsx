import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { PanelDetalleDia } from "./PanelDetalleDia";
import type { DetalleDiaResponse } from "../api/types";

function makeDetalle(overrides: Partial<DetalleDiaResponse> = {}): DetalleDiaResponse {
  return {
    fecha: "2026-06-15",
    kwh_dia: 12.5,
    kwh_mismo_dia_anio_ant: 10.0,
    kwh_promedio_zona: 9.5,
    n_vecinos: 5,
    ...overrides,
  };
}

describe("PanelDetalleDia", () => {
  it("muestra el estado de carga cuando loading=true", () => {
    render(
      <PanelDetalleDia fecha="2026-06-15" detalle={null} loading={true} onCerrar={() => {}} />
    );
    expect(screen.getByText(/Cargando detalle/)).not.toBeNull();
    expect(screen.queryByTestId("detalle-kwh-dia")).toBeNull();
  });

  it("muestra kwh_dia, kwh_mismo_dia_anio_ant y kwh_promedio_zona cuando hay datos", () => {
    render(
      <PanelDetalleDia
        fecha="2026-06-15"
        detalle={makeDetalle()}
        loading={false}
        onCerrar={() => {}}
      />
    );
    expect(screen.getByTestId("detalle-kwh-dia").textContent).toMatch(/12.5 kWh/);
    expect(screen.getByTestId("detalle-kwh-anio-ant").textContent).toMatch(/10.0 kWh/);
    expect(screen.getByTestId("detalle-kwh-zona").textContent).toMatch(/9.5 kWh/);
  });

  it("muestra '—' en zona cuando n_vecinos < 5 (privacidad)", () => {
    render(
      <PanelDetalleDia
        fecha="2026-06-15"
        detalle={makeDetalle({ kwh_promedio_zona: null, n_vecinos: 3 })}
        loading={false}
        onCerrar={() => {}}
      />
    );
    const zonaCard = screen.getByTestId("detalle-kwh-zona");
    expect(zonaCard.textContent).toMatch(/—/);
  });

  it("muestra 'Sin dato' cuando kwh_dia es null con suficientes vecinos", () => {
    render(
      <PanelDetalleDia
        fecha="2026-06-10"
        detalle={makeDetalle({ kwh_dia: null })}
        loading={false}
        onCerrar={() => {}}
      />
    );
    expect(screen.getByTestId("detalle-kwh-dia").textContent).toMatch(/Sin dato/);
  });

  it("muestra la fecha formateada en el título", () => {
    render(
      <PanelDetalleDia fecha="2026-06-15" detalle={null} loading={true} onCerrar={() => {}} />
    );
    expect(screen.getByText(/15 jun 2026/)).not.toBeNull();
  });

  it("llama a onCerrar al hacer click en Cerrar", () => {
    const onCerrar = vi.fn();
    render(
      <PanelDetalleDia fecha="2026-06-15" detalle={makeDetalle()} loading={false} onCerrar={onCerrar} />
    );
    fireEvent.click(screen.getByText("Cerrar"));
    expect(onCerrar).toHaveBeenCalledOnce();
  });
});
