import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HomePage } from "./HomePage";
import type { FacturaDatosResponse, HomeResponse, ObjetivoEstadoResponse } from "../api/types";

vi.mock("../api/home", () => ({ fetchHome: vi.fn() }));
vi.mock("../api/usuario", () => ({ fetchPerfil: vi.fn() }));
vi.mock("../api/objetivos", () => ({ fetchObjetivoEstado: vi.fn() }));
vi.mock("../api/factura", () => ({ fetchFacturaDatos: vi.fn() }));

import { fetchHome } from "../api/home";
import { fetchPerfil } from "../api/usuario";
import { fetchObjetivoEstado } from "../api/objetivos";
import { fetchFacturaDatos } from "../api/factura";

const home: HomeResponse = {
  consumo_mes: { total_kwh: 142, vs_mes_anterior_pct: -8, vs_anio_anterior_pct: 3 },
  comparacion_zona: { promedio_vecinos_kwh: 160, n_vecinos: 8, diferencia_pct: -12, serie: [] },
  proyeccion: {
    mes: "2026-06",
    metodo_aplicado: "promedio_diario",
    bandera_confianza: "alta",
    rango_inferior_kwh: 195,
    rango_superior_kwh: 225,
  },
  datos_hasta: "2026-06-28",
  timestamp: "2026-06-30T12:00:00Z",
};

const estado: ObjetivoEstadoResponse = {
  objetivo_kwh: 200,
  promedio_vecinos_kwh: null,
  n_vecinos: 0,
  diferencia_pct: null,
  dias_transcurridos: 10,
  dias_objetivo_consumidos: 8,
  texto_dinamico: "en_ritmo",
  excedente_kwh: null,
  consumo_diario_real_kwh: null,
  consumo_diario_objetivo_kwh: null,
  consumo_acumulado_kwh: 80,
  consumo_promedio_diario_kwh: 8,
};

const factura: FacturaDatosResponse = {
  total_deuda: 18420.5,
  pago_online: false,
  cliente_id: null,
  contrato_id: null,
  documentos: [
    { periodo: "06/2026", importe: 18420.5, fecha_vencimiento: "2026-07-20", estado: null, url_pdf: null },
  ],
};

beforeEach(() => {
  vi.mocked(fetchHome).mockResolvedValue(home);
  vi.mocked(fetchPerfil).mockResolvedValue({
    nombre: "Pedro",
    nro_suministro: "2817670",
    suministro_id: "SRV-2817670",
    tarifa_codigo: "T1",
  });
  vi.mocked(fetchObjetivoEstado).mockResolvedValue(estado);
  vi.mocked(fetchFacturaDatos).mockResolvedValue(factura);
});

describe("HomePage tablero", () => {
  it("muestra las cuatro tarjetas del tablero", async () => {
    render(<HomePage token="t" suministroId="SRV-2817670" />);

    await waitFor(() => expect(screen.getByText("142.0")).not.toBeNull());
    expect(screen.getByRole("region", { name: "consumo del mes" })).not.toBeNull();
    expect(screen.getByRole("region", { name: "objetivo del mes" })).not.toBeNull();
    expect(screen.getByRole("region", { name: "deuda" })).not.toBeNull();
    expect(screen.getByRole("region", { name: "comparación de zona" })).not.toBeNull();
  });

  it("ordena las tarjetas: consumo, objetivo, deuda, zona", async () => {
    render(<HomePage token="t" suministroId="SRV-2817670" />);

    await waitFor(() => expect(screen.getByText("142.0")).not.toBeNull());
    const nombres = screen.getAllByRole("region").map((r) => r.getAttribute("aria-label"));
    expect(nombres).toEqual([
      "consumo del mes",
      "objetivo del mes",
      "deuda",
      "comparación de zona",
    ]);
  });

  it("navega a factura desde la card de deuda", async () => {
    const onNavegar = vi.fn();
    render(<HomePage token="t" suministroId="SRV-2817670" onNavegar={onNavegar} />);

    const verFactura = await screen.findByRole("button", { name: /ver factura/i });
    await userEvent.click(verFactura);
    expect(onNavegar).toHaveBeenCalledWith("factura");
  });
});
