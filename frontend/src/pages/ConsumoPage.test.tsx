import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { ConsumoPage } from "./ConsumoPage";
import * as consumoApi from "../api/consumo";

vi.mock("../api/consumo");

const TOKEN = "tok";
const SUMINISTRO = "S001";

const SERIE_VACIA = { serie: [], datos_hasta: null };
const COMPARACION_VACIA = {
  mes_actual: { mes: "2026-06-01", serie: [], total_kwh: null },
  mes_anterior: { mes: "2026-05-01", serie: [], total_kwh: null },
  mismo_mes_anio_anterior: { mes: "2025-06-01", serie: [], total_kwh: null },
  datos_hasta: null,
};

beforeEach(() => {
  vi.mocked(consumoApi.fetchSerieDiaria).mockResolvedValue(SERIE_VACIA);
  vi.mocked(consumoApi.fetchComparacion).mockResolvedValue(COMPARACION_VACIA);
  vi.mocked(consumoApi.fetchDetalleDia).mockResolvedValue({
    fecha: "2026-06-15",
    kwh_dia: 12.5,
    kwh_mismo_dia_anio_ant: 10.0,
    kwh_promedio_zona: 9.5,
    n_vecinos: 5,
  });
});

describe("ConsumoPage", () => {
  it("no muestra el panel de detalle en el estado inicial", async () => {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByText("Cargando consumo...")).toBeNull());
    expect(screen.queryByTestId("panel-detalle")).toBeNull();
  });

  it("llama a fetchSerieDiaria y fetchComparacion al montar", async () => {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => {
      expect(vi.mocked(consumoApi.fetchSerieDiaria)).toHaveBeenCalledWith(
        TOKEN,
        SUMINISTRO,
        expect.stringMatching(/^\d{4}-\d{2}-01$/),
        expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/)
      );
      expect(vi.mocked(consumoApi.fetchComparacion)).toHaveBeenCalledWith(
        TOKEN,
        SUMINISTRO,
        expect.stringMatching(/^\d{4}-\d{2}$/)
      );
    });
  });

  it("fetchDetalleDia no es llamado en el estado inicial (sin click)", async () => {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByText("Cargando consumo...")).toBeNull());
    expect(vi.mocked(consumoApi.fetchDetalleDia)).not.toHaveBeenCalled();
  });
});
