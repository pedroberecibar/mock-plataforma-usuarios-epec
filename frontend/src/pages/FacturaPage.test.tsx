import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import { FacturaPage } from "./FacturaPage";
import * as facturaApi from "../api/factura";
import type { FacturaDatosResponse, FacturaDocumento } from "../api/types";

vi.mock("../api/factura");

const TOKEN = "tok";

function doc(overrides: Partial<FacturaDocumento> = {}): FacturaDocumento {
  return {
    periodo: "07/2026",
    importe: 1000,
    fecha_vencimiento: null,
    estado: "pagar",
    url_pdf: null,
    ...overrides,
  };
}

function cuenta(documentos: FacturaDocumento[]): FacturaDatosResponse {
  return {
    total_deuda: documentos.reduce((s, d) => s + (d.importe ?? 0), 0),
    pago_online: true,
    documentos,
  };
}

function enDias(n: number): string {
  const f = new Date();
  f.setDate(f.getDate() + n);
  return f.toISOString().slice(0, 10);
}

beforeEach(() => {
  vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue(cuenta([]));
  vi.mocked(facturaApi.evaluarVencimiento).mockResolvedValue(undefined);
});

describe("FacturaPage — enlace a EPEC", () => {
  it("muestra el enlace al portal de EPEC cuando hay deuda", async () => {
    vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue(cuenta([doc()]));
    render(<FacturaPage token={TOKEN} />);
    const link = (await screen.findByTestId("enlace-epec")) as HTMLAnchorElement;
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

describe("FacturaPage — Design system", () => {
  it("renderiza PageHeader con título 'Mi Factura'", () => {
    render(<FacturaPage token={TOKEN} />);
    const banner = screen.getByRole("banner");
    expect(within(banner).getByText("Mi Factura")).not.toBeNull();
  });
});

describe("FacturaPage — deuda total y listado", () => {
  it("muestra el total de deuda y un item por factura", async () => {
    vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue(
      cuenta([doc({ periodo: "07/2026", importe: 100 }), doc({ periodo: "06/2026", importe: 50 })])
    );
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() => expect(screen.getByText(/Período 07\/2026/)).not.toBeNull());
    expect(screen.getByText(/Período 06\/2026/)).not.toBeNull();
  });
});

describe("FacturaPage — banner de vencimiento", () => {
  it("no muestra banner cuando no hay facturas", async () => {
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() => expect(vi.mocked(facturaApi.fetchFacturaDatos)).toHaveBeenCalled());
    expect(screen.queryByTestId("banner-vencimiento")).toBeNull();
  });

  it("muestra banner cuando faltan ≤5 días para el vencimiento", async () => {
    vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue(
      cuenta([doc({ fecha_vencimiento: enDias(3) })])
    );
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() => expect(screen.getByTestId("banner-vencimiento")).not.toBeNull());
  });

  it("no muestra banner cuando faltan >5 días para el vencimiento", async () => {
    vi.mocked(facturaApi.fetchFacturaDatos).mockResolvedValue(
      cuenta([doc({ fecha_vencimiento: enDias(10) })])
    );
    render(<FacturaPage token={TOKEN} />);
    await waitFor(() => expect(vi.mocked(facturaApi.fetchFacturaDatos)).toHaveBeenCalled());
    expect(screen.queryByTestId("banner-vencimiento")).toBeNull();
  });
});
