import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, within, cleanup } from "@testing-library/react";
import { CuentaPage } from "./CuentaPage";
import * as cuentaApi from "../api/cuenta";
import type { CuentaResponse } from "../api/types";

vi.mock("../api/cuenta");

const TOKEN = "tok";

const CUENTA_COMPLETA: CuentaResponse = {
  personales: {
    nombre_o_razon_social: "Juana Pérez",
    tipo_documento: "DNI",
    nro_documento_masked: "****1815",
    cuit_masked: "********153",
    email: "juana@example.com",
  },
  suministro: {
    numero: "SRV-2817670",
    estado_servicio: "Activo",
    direccion: "Av. Siempre Viva 742",
    barrio: "Centro",
    localidad: "Córdoba",
    cp: "5000",
  },
  tarifa: {
    codigo: "140",
    descripcion: "1.a/f RESIDENCIAL",
    grupo_tarifario: "T1",
    clase: "1",
    clase_descripcion: "1 a-b-f Casas de familia",
    tension: "Baja",
  },
  medidor: {
    numero: "MED-99",
    marca: "CLOU",
    fase: "Monofásico",
    inteligente_desde: "2023-03-10",
  },
};

beforeEach(() => {
  vi.mocked(cuentaApi.fetchCuenta).mockResolvedValue(CUENTA_COMPLETA);
});

afterEach(() => cleanup());

describe("CuentaPage — estructura y carga", () => {
  it("renderiza PageHeader con título 'Mi cuenta'", async () => {
    render(<CuentaPage token={TOKEN} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    const banner = screen.getByRole("banner");
    expect(within(banner).getByText("Mi cuenta")).not.toBeNull();
  });

  it("muestra skeletons mientras carga", () => {
    vi.mocked(cuentaApi.fetchCuenta).mockReturnValue(new Promise(() => {}));
    render(<CuentaPage token={TOKEN} />);
    expect(screen.getAllByTestId("skeleton-block").length).toBeGreaterThan(0);
  });

  it("llama a fetchCuenta con el token al montar", async () => {
    render(<CuentaPage token={TOKEN} />);
    await waitFor(() =>
      expect(vi.mocked(cuentaApi.fetchCuenta)).toHaveBeenCalledWith(TOKEN),
    );
  });
});

describe("CuentaPage — datos completos", () => {
  it("muestra las 4 secciones agrupadas", async () => {
    render(<CuentaPage token={TOKEN} />);
    expect(await screen.findByText("Datos personales")).not.toBeNull();
    expect(screen.getByText("Suministro")).not.toBeNull();
    // "Tarifa" aparece como título de sección y como etiqueta de campo (diseño intencional)
    expect(screen.getAllByText("Tarifa").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Medidor")).not.toBeNull();
  });

  it("muestra el nombre, suministro y valores enmascarados", async () => {
    render(<CuentaPage token={TOKEN} />);
    expect((await screen.findAllByText("Juana Pérez")).length).toBeGreaterThan(0);
    expect(screen.getAllByText("SRV-2817670").length).toBeGreaterThan(0);
    expect(screen.getByText("****1815")).not.toBeNull();
    expect(screen.getByText("********153")).not.toBeNull();
    expect(screen.getByText("1.a/f RESIDENCIAL")).not.toBeNull();
    expect(screen.getByText("Monofásico")).not.toBeNull();
  });
});

describe("CuentaPage — campos null", () => {
  it("muestra 'No informado' para campos null y no rompe con DNI null (empresa)", async () => {
    vi.mocked(cuentaApi.fetchCuenta).mockResolvedValue({
      ...CUENTA_COMPLETA,
      personales: {
        nombre_o_razon_social: "Comercial GC SA",
        tipo_documento: null,
        nro_documento_masked: null,
        cuit_masked: "********153",
        email: null,
      },
    });
    render(<CuentaPage token={TOKEN} />);
    expect((await screen.findAllByText("Comercial GC SA")).length).toBeGreaterThan(0);
    expect(screen.getAllByText("No informado").length).toBeGreaterThan(0);
  });
});

describe("CuentaPage — errores", () => {
  it("muestra EmptyState cuando el backend responde 503 (no configurado)", async () => {
    vi.mocked(cuentaApi.fetchCuenta).mockRejectedValue(new Error("no_configurado"));
    render(<CuentaPage token={TOKEN} />);
    const status = await screen.findByRole("status");
    expect(within(status).getByText("Tus datos no están disponibles por ahora")).not.toBeNull();
  });

  it("muestra EmptyState cuando el backend responde 404 (sin datos)", async () => {
    vi.mocked(cuentaApi.fetchCuenta).mockRejectedValue(new Error("sin_datos"));
    render(<CuentaPage token={TOKEN} />);
    const status = await screen.findByRole("status");
    expect(within(status).getByText("No encontramos datos de tu suministro")).not.toBeNull();
  });
});
