import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { ObjetivosPage } from "./ObjetivosPage";
import * as objetivosApi from "../api/objetivos";
import * as homeApi from "../api/home";
import type { HomeResponse } from "../api/types";

vi.mock("../api/objetivos");
vi.mock("../api/home");

const TOKEN = "tok";
const SUMINISTRO = "S001";

const OBJETIVO = { valor_kwh: 200, origen: "manual", vigente_desde: "2026-06-01" };

function makeHome(total_kwh: number | null): HomeResponse {
  return {
    consumo_mes: { total_kwh, vs_mes_anterior_pct: null, vs_anio_anterior_pct: null },
    comparacion_zona: { promedio_vecinos_kwh: null, n_vecinos: 0, diferencia_pct: null },
    proyeccion: { mes: "2026-06", metodo_aplicado: "lineal", bandera_confianza: "alta", rango_inferior_kwh: null, rango_superior_kwh: null },
    datos_hasta: null,
    timestamp: "2026-06-18T12:00:00Z",
  };
}

beforeEach(() => {
  vi.mocked(objetivosApi.fetchObjetivo).mockResolvedValue(OBJETIVO);
  vi.mocked(homeApi.fetchHome).mockResolvedValue(makeHome(120));
});

describe("ObjetivosPage — barra de progreso", () => {
  it("muestra la barra de progreso cuando hay objetivo y consumo", async () => {
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("progressbar")).not.toBeNull());
  });

  it("muestra el porcentaje consumido (60% = 120 de 200 kWh)", async () => {
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByText(/60\s*%/)).not.toBeNull());
  });

  it("muestra los kWh acumulados vs objetivo", async () => {
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByText(/120.*200\s*kWh/)).not.toBeNull());
  });

  it("muestra advertencia cuando el consumo supera el 80% del objetivo (180/200)", async () => {
    vi.mocked(homeApi.fetchHome).mockResolvedValue(makeHome(180));
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("alert")).not.toBeNull());
  });

  it("muestra alerta de superado cuando el consumo iguala o supera el objetivo (200/200)", async () => {
    vi.mocked(homeApi.fetchHome).mockResolvedValue(makeHome(200));
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert.textContent).toMatch(/superado|objetivo alcanzado/i);
    });
  });

  it("no muestra barra de progreso cuando no hay objetivo configurado", async () => {
    vi.mocked(objetivosApi.fetchObjetivo).mockResolvedValue(null);
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByRole("progressbar")).toBeNull());
  });

  it("no muestra barra de progreso cuando el consumo del mes es null", async () => {
    vi.mocked(homeApi.fetchHome).mockResolvedValue(makeHome(null));
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByRole("progressbar")).toBeNull());
  });
});
