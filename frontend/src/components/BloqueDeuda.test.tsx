import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BloqueDeuda } from "./BloqueDeuda";
import type { FacturaDatosResponse, FacturaDocumento } from "../api/types";

function datos(over: Partial<FacturaDatosResponse>): FacturaDatosResponse {
  return {
    total_deuda: 0,
    pago_online: false,
    cliente_id: null,
    contrato_id: null,
    documentos: [],
    ...over,
  };
}

function doc(over: Partial<FacturaDocumento>): FacturaDocumento {
  return {
    periodo: "06/2026",
    importe: 1000,
    fecha_vencimiento: null,
    estado: null,
    url_pdf: null,
    ...over,
  };
}

describe("BloqueDeuda", () => {
  it("sin datos cargados muestra un guión, no un estado de 'al día'", () => {
    render(<BloqueDeuda datos={null} />);
    expect(screen.getByText("—")).not.toBeNull();
    expect(screen.queryByText(/al día/i)).toBeNull();
  });

  it("sin facturas pendientes muestra 'Estás al día'", () => {
    render(<BloqueDeuda datos={datos({ documentos: [] })} />);
    expect(screen.getByText(/al día/i)).not.toBeNull();
  });

  it("con deuda muestra importe y cantidad de facturas", () => {
    render(
      <BloqueDeuda
        datos={datos({ total_deuda: 18420.5, documentos: [doc({}), doc({})] })}
      />,
    );
    expect(screen.getByText(/18\.420/)).not.toBeNull();
    expect(screen.getByText(/2 facturas pendientes/i)).not.toBeNull();
  });

  it("muestra el chip de urgencia cuando el vencimiento está próximo", () => {
    const pronto = new Date();
    pronto.setDate(pronto.getDate() + 2);
    const iso = pronto.toISOString().slice(0, 10);
    render(
      <BloqueDeuda
        datos={datos({ total_deuda: 1000, documentos: [doc({ fecha_vencimiento: iso })] })}
      />,
    );
    expect(screen.getByText(/faltan \d+ días|vence (hoy|mañana)/i)).not.toBeNull();
  });

  it("navega a factura al tocar el CTA", async () => {
    const onNavegar = vi.fn();
    render(
      <BloqueDeuda
        datos={datos({ total_deuda: 1000, documentos: [doc({})] })}
        onNavegar={onNavegar}
      />,
    );
    await userEvent.click(screen.getByRole("button", { name: /ver factura/i }));
    expect(onNavegar).toHaveBeenCalledWith("factura");
  });

  it("tiene aria-label de sección", () => {
    render(<BloqueDeuda datos={datos({})} />);
    expect(screen.getByRole("region", { name: "deuda" })).not.toBeNull();
  });
});
