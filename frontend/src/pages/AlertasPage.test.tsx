import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import { AlertasPage } from "./AlertasPage";
import * as alertasApi from "../api/alertas";

vi.mock("../api/alertas");

const TOKEN = "tok";

const CONFIG_DEFAULT = [
  { tipo: "factura_disponible", habilitado: true },
  { tipo: "vencimiento_proximo", habilitado: false },
  { tipo: "consumo_anomalo", habilitado: true },
];

beforeEach(() => {
  vi.mocked(alertasApi.fetchAlertasConfig).mockResolvedValue(CONFIG_DEFAULT);
  vi.mocked(alertasApi.patchAlertaConfig).mockResolvedValue(undefined);
});

describe("AlertasPage — Design system (Etapa 7)", () => {
  it("renderiza PageHeader con título 'Alertas'", async () => {
    render(<AlertasPage token={TOKEN} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    const banner = screen.getByRole("banner");
    expect(within(banner).getByText("Alertas")).not.toBeNull();
  });

  it("muestra skeletons de carga en lugar de texto plano", () => {
    vi.mocked(alertasApi.fetchAlertasConfig).mockReturnValue(new Promise(() => {}));
    render(<AlertasPage token={TOKEN} />);
    expect(screen.getAllByTestId("skeleton-block").length).toBeGreaterThan(0);
  });
});

describe("AlertasPage — toggles de configuración", () => {
  it("muestra las 3 alertas disponibles", async () => {
    render(<AlertasPage token={TOKEN} />);
    await waitFor(() => expect(screen.getByText("Factura disponible")).not.toBeNull());
    expect(screen.getByText("Vencimiento próximo")).not.toBeNull();
    expect(screen.getByText("Consumo inusual")).not.toBeNull();
  });

  it("llama a fetchAlertasConfig al montar", async () => {
    render(<AlertasPage token={TOKEN} />);
    await waitFor(() =>
      expect(vi.mocked(alertasApi.fetchAlertasConfig)).toHaveBeenCalledWith(TOKEN)
    );
  });
});
