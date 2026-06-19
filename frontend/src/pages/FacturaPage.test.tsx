import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { FacturaPage } from "./FacturaPage";
import * as facturaApi from "../api/factura";

vi.mock("../api/factura");

const TOKEN = "tok";

beforeEach(() => {
  vi.mocked(facturaApi.fetchLinkFactura).mockResolvedValue("https://epec.com.ar/factura");
  vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue({ fecha_vencimiento: null });
  vi.mocked(facturaApi.evaluarVencimiento).mockResolvedValue(undefined);
});

describe("FacturaPage — banner de vencimiento", () => {
  it("no muestra banner cuando fecha_vencimiento es null", async () => {
    vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue({ fecha_vencimiento: null });
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() =>
      expect(vi.mocked(facturaApi.fetchFacturaDatos)).toHaveBeenCalled()
    );
    expect(screen.queryByTestId("banner-vencimiento")).toBeNull();
  });

  it("muestra banner cuando faltan ≤5 días para el vencimiento", async () => {
    // Simular vencimiento en 3 días
    const fecha = new Date();
    fecha.setDate(fecha.getDate() + 3);
    const fechaStr = fecha.toISOString().slice(0, 10);

    vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue({ fecha_vencimiento: fechaStr });
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() =>
      expect(screen.queryByTestId("banner-vencimiento")).not.toBeNull()
    );
    expect(screen.getByRole("alert")).not.toBeNull();
  });

  it("no muestra banner cuando faltan >5 días para el vencimiento", async () => {
    const fecha = new Date();
    fecha.setDate(fecha.getDate() + 10);
    const fechaStr = fecha.toISOString().slice(0, 10);

    vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue({ fecha_vencimiento: fechaStr });
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() =>
      expect(vi.mocked(facturaApi.fetchFacturaDatos)).toHaveBeenCalled()
    );
    expect(screen.queryByTestId("banner-vencimiento")).toBeNull();
  });

  it("llama a evaluarVencimiento al montar", async () => {
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() =>
      expect(vi.mocked(facturaApi.evaluarVencimiento)).toHaveBeenCalledWith(TOKEN)
    );
  });
});
