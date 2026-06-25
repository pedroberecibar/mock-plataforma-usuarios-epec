import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within, fireEvent } from "@testing-library/react";
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

const SERIE_HORARIA_RESP = {
  fecha: "2026-06-15",
  serie: Array.from({ length: 24 }, (_, h) => ({ hora: h, kwh: 0.3 + (h === 20 ? 0.5 : 0) })),
};

beforeEach(() => {
  vi.mocked(consumoApi.fetchSerieDiaria).mockResolvedValue(SERIE_VACIA);
  vi.mocked(consumoApi.fetchComparacion).mockResolvedValue(COMPARACION_VACIA);
  vi.mocked(consumoApi.fetchAnomalia).mockResolvedValue(null);
  vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(null);
  vi.mocked(objetivosApi.fetchObjetivo).mockResolvedValue(null);
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

  it("muestra las cards de comparación histórica en fila superior", async () => {
    const COMPARACION_CON_DATOS = {
      mes_actual:              { mes: "2026-06-01", serie: [], total_kwh: 252.8 },
      mes_anterior:            { mes: "2026-05-01", serie: [], total_kwh: 333.3 },
      mismo_mes_anio_anterior: { mes: "2025-06-01", serie: [], total_kwh: 444.7 },
      zona_mes_actual:         { promedio_vecinos_kwh: null, n_vecinos: 0, diferencia_pct: null, serie: [] },
      datos_hasta: null,
    };
    vi.mocked(consumoApi.fetchComparacion).mockResolvedValue(COMPARACION_CON_DATOS);
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    expect(screen.getByText("Consumo mes actual")).not.toBeNull();
    expect(screen.getByText("Mes anterior")).not.toBeNull();
    expect(screen.getByText("Mismo mes año anterior")).not.toBeNull();
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

  it("carga el objetivo vigente al montar (fetchObjetivo)", async () => {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() =>
      expect(vi.mocked(objetivosApi.fetchObjetivo)).toHaveBeenCalledWith(TOKEN)
    );
  });

  it("muestra la card de Objetivo arriba del Resumen del mes", async () => {
    vi.mocked(objetivosApi.fetchObjetivo).mockResolvedValue({
      valor_kwh: 200, origen: "manual", vigente_desde: "2026-06-01",
    });
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    const card = screen.getByLabelText("Objetivo de consumo");
    const resumen = screen.getByText("Día más alto");
    // La card aparece antes en el DOM que el "Resumen del mes".
    expect(card.compareDocumentPosition(resumen) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("dispara onEditarObjetivo al hacer click en 'Editar objetivo'", async () => {
    const onEditarObjetivo = vi.fn();
    vi.mocked(objetivosApi.fetchObjetivo).mockResolvedValue({
      valor_kwh: 200, origen: "manual", vigente_desde: "2026-06-01",
    });
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} onEditarObjetivo={onEditarObjetivo} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    fireEvent.click(screen.getByText(/Editar objetivo/i));
    expect(onEditarObjetivo).toHaveBeenCalledTimes(1);
  });
});
