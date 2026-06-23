import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import { FacturaPage } from "./FacturaPage";
import * as facturaApi from "../api/factura";

vi.mock("../api/factura");

const TOKEN = "tok";

beforeEach(() => {
  vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue({ fecha_vencimiento: null });
  vi.mocked(facturaApi.evaluarVencimiento).mockResolvedValue(undefined);
});

describe("FacturaPage — enlace a EPEC", () => {
  it("muestra el enlace al portal de EPEC", () => {
    render(<FacturaPage token={TOKEN} />);
    const link = screen.getByTestId("enlace-epec") as HTMLAnchorElement;
    expect(link.href).toBe("https://www.epec.com.ar/tramites/pagos");
    expect(link.target).toBe("_blank");
  });

  it("llama a evaluarVencimiento al montar", async () => {
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() =>
      expect(vi.mocked(facturaApi.evaluarVencimiento)).toHaveBeenCalledWith(TOKEN)
    );
  });
});

describe("FacturaPage — Design system (Etapa 7)", () => {
  it("renderiza PageHeader con título 'Mi Factura'", () => {
    render(<FacturaPage token={TOKEN} />);
    const banner = screen.getByRole("banner");
    expect(within(banner).getByText("Mi Factura")).not.toBeNull();
  });
});

describe("FacturaPage — banner de vencimiento", () => {
  it("no muestra banner cuando fecha_vencimiento es null", async () => {
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() =>
      expect(vi.mocked(facturaApi.fetchFacturaDatos)).toHaveBeenCalled()
    );
    expect(screen.queryByTestId("banner-vencimiento")).toBeNull();
  });

  it("muestra banner cuando faltan ≤5 días para el vencimiento", async () => {
    const fecha = new Date();
    fecha.setDate(fecha.getDate() + 3);
    vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue({
      fecha_vencimiento: fecha.toISOString().slice(0, 10),
    });
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() =>
      expect(screen.getByTestId("banner-vencimiento")).not.toBeNull()
    );
  });

  it("no muestra banner cuando faltan >5 días para el vencimiento", async () => {
    const fecha = new Date();
    fecha.setDate(fecha.getDate() + 10);
    vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue({
      fecha_vencimiento: fecha.toISOString().slice(0, 10),
    });
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() =>
      expect(vi.mocked(facturaApi.fetchFacturaDatos)).toHaveBeenCalled()
    );
    expect(screen.queryByTestId("banner-vencimiento")).toBeNull();
  });
});
