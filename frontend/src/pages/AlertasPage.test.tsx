import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within, fireEvent } from "@testing-library/react";
import { AlertasPage } from "./AlertasPage";
import * as alertasApi from "../api/alertas";

vi.mock("../api/alertas");

const TOKEN = "tok";

const CONFIG_DEFAULT = [
  { tipo: "factura_disponible", habilitado: true },
  { tipo: "vencimiento_proximo", habilitado: false },
  { tipo: "consumo_anomalo", habilitado: true },
];

const CONFIG_TODAS_APAGADAS = [
  { tipo: "factura_disponible", habilitado: false },
  { tipo: "vencimiento_proximo", habilitado: false },
  { tipo: "consumo_anomalo", habilitado: false },
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

describe("AlertasPage — campana maestra (apagar/encender todas)", () => {
  it("ofrece 'Activar todas' cuando todas las alertas están apagadas", async () => {
    vi.mocked(alertasApi.fetchAlertasConfig).mockResolvedValue(CONFIG_TODAS_APAGADAS);
    render(<AlertasPage token={TOKEN} />);
    expect(await screen.findByRole("button", { name: /activar todas/i })).not.toBeNull();
  });

  it("ofrece 'Desactivar todas' cuando hay alguna alerta encendida", async () => {
    render(<AlertasPage token={TOKEN} />);
    expect(await screen.findByRole("button", { name: /desactivar todas/i })).not.toBeNull();
  });

  it("apaga todas las alertas al hacer click cuando había alguna encendida", async () => {
    render(<AlertasPage token={TOKEN} />);
    const bell = await screen.findByRole("button", { name: /desactivar todas/i });
    fireEvent.click(bell);
    await waitFor(() => {
      expect(vi.mocked(alertasApi.patchAlertaConfig)).toHaveBeenCalledWith(TOKEN, "factura_disponible", false);
      expect(vi.mocked(alertasApi.patchAlertaConfig)).toHaveBeenCalledWith(TOKEN, "vencimiento_proximo", false);
      expect(vi.mocked(alertasApi.patchAlertaConfig)).toHaveBeenCalledWith(TOKEN, "consumo_anomalo", false);
    });
    expect(await screen.findByRole("button", { name: /activar todas/i })).not.toBeNull();
  });

  it("enciende todas las alertas al hacer click cuando estaban todas apagadas", async () => {
    vi.mocked(alertasApi.fetchAlertasConfig).mockResolvedValue(CONFIG_TODAS_APAGADAS);
    render(<AlertasPage token={TOKEN} />);
    const bell = await screen.findByRole("button", { name: /activar todas/i });
    fireEvent.click(bell);
    await waitFor(() => {
      expect(vi.mocked(alertasApi.patchAlertaConfig)).toHaveBeenCalledWith(TOKEN, "factura_disponible", true);
      expect(vi.mocked(alertasApi.patchAlertaConfig)).toHaveBeenCalledWith(TOKEN, "vencimiento_proximo", true);
      expect(vi.mocked(alertasApi.patchAlertaConfig)).toHaveBeenCalledWith(TOKEN, "consumo_anomalo", true);
    });
  });
});
