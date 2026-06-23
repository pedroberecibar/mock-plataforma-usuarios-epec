import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import { ConsumoPage } from "./ConsumoPage";
import * as consumoApi from "../api/consumo";
import * as objetivosApi from "../api/objetivos";

vi.mock("../api/consumo");
vi.mock("../api/objetivos");

const TOKEN = "tok";
const SUMINISTRO = "S001";

const SERIE_VACIA = { serie: [], datos_hasta: null };
const COMPARACION_VACIA = {
  mes_actual: { mes: "2026-06-01", serie: [], total_kwh: null },
  mes_anterior: { mes: "2026-05-01", serie: [], total_kwh: null },
  mismo_mes_anio_anterior: { mes: "2025-06-01", serie: [], total_kwh: null },
  zona_mes_actual: { promedio_vecinos_kwh: null, n_vecinos: 0, diferencia_pct: null, serie: [] },
  datos_hasta: null,
};

const HORA_PICO_RESP = {
  hora_pico: 20,
  kwh_promedio: 0.8,
  perfil_24h: Array.from({ length: 24 }, (_, h) => ({ hora: h, kwh: h === 20 ? 0.8 : 0.3 })),
};

const SERIE_HORARIA_RESP = {
  fecha: "2026-06-15",
  serie: Array.from({ length: 24 }, (_, h) => ({ hora: h, kwh: 0.3 + (h === 20 ? 0.5 : 0) })),
};

beforeEach(() => {
  vi.mocked(consumoApi.fetchSerieDiaria).mockResolvedValue(SERIE_VACIA);
  vi.mocked(consumoApi.fetchComparacion).mockResolvedValue(COMPARACION_VACIA);
  vi.mocked(consumoApi.fetchAnomalia).mockResolvedValue(null);
  vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(null);
  vi.mocked(consumoApi.fetchHoraPico).mockResolvedValue(HORA_PICO_RESP);
  vi.mocked(consumoApi.fetchSerieHoraria).mockResolvedValue(SERIE_HORARIA_RESP);
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
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
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
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    expect(vi.mocked(consumoApi.fetchDetalleDia)).not.toHaveBeenCalled();
  });

  it("llama a fetchHoraPico al montar y muestra la card hora pico", async () => {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => {
      expect(vi.mocked(consumoApi.fetchHoraPico)).toHaveBeenCalledWith(
        TOKEN,
        expect.stringMatching(/^\d{4}-\d{2}$/)
      );
    });
    await waitFor(() => expect(screen.getByText("Hora pico del mes")).not.toBeNull());
    expect(screen.getByText("20:00 hs")).not.toBeNull();
  });

  it("no muestra card hora pico cuando fetchHoraPico retorna null", async () => {
    vi.mocked(consumoApi.fetchHoraPico).mockResolvedValue(null);
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    expect(screen.queryByText("Hora pico del mes")).toBeNull();
  });

  it("muestra skeletons de carga en lugar de texto plano", () => {
    vi.mocked(consumoApi.fetchSerieDiaria).mockReturnValue(new Promise(() => {}));
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    expect(screen.getAllByTestId("skeleton-block").length).toBeGreaterThan(0);
    expect(screen.queryByText("Cargando consumo...")).toBeNull();
  });

  it("renderiza PageHeader con título 'Mi Consumo'", async () => {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    const banner = screen.getByRole("banner");
    expect(within(banner).getByText("Mi Consumo")).not.toBeNull();
  });

  it("muestra AlertBanner de error en lugar de texto plano", async () => {
    vi.mocked(consumoApi.fetchSerieDiaria).mockRejectedValue(new Error("Sin conexión"));
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("alert")).not.toBeNull());
    expect(screen.getByText(/Sin conexión/)).not.toBeNull();
  });
});
