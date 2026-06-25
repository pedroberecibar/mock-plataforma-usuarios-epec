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
    expect(screen.getByText("Mes anterior")).not.toBeNull();
    expect(screen.getByText("Mismo mes año anterior")).not.toBeNull();
  });

  it("no duplica 'Promedio diario' en el resumen del mes", async () => {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    expect(screen.getAllByText("Promedio diario").length).toBe(1);
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

describe("ConsumoPage — filtro por mes", () => {
  async function renderListo() {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
  }

  function mesAnterior(): string {
    const m = screen.getByRole("combobox") as HTMLSelectElement;
    const opciones = Array.from(m.options).map((o) => o.value);
    return opciones[1]; // el segundo es el mes anterior al actual
  }

  it("renderiza un selector de mes", async () => {
    await renderListo();
    expect(screen.getByRole("combobox")).not.toBeNull();
  });

  it("al cambiar el mes, re-consulta comparación, anomalía y estado de objetivo con ese mes", async () => {
    await renderListo();
    const target = mesAnterior();
    vi.mocked(consumoApi.fetchComparacion).mockClear();
    vi.mocked(consumoApi.fetchAnomalia).mockClear();
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockClear();

    fireEvent.change(screen.getByRole("combobox"), { target: { value: target } });

    await waitFor(() => {
      expect(vi.mocked(consumoApi.fetchComparacion)).toHaveBeenCalledWith(TOKEN, SUMINISTRO, target);
      expect(vi.mocked(consumoApi.fetchAnomalia)).toHaveBeenCalledWith(TOKEN, target);
      expect(vi.mocked(objetivosApi.fetchObjetivoEstado)).toHaveBeenCalledWith(TOKEN, target);
    });
  });

  it("al cambiar a un mes pasado, pide la serie diaria del primer al último día de ese mes", async () => {
    await renderListo();
    const target = mesAnterior();
    vi.mocked(consumoApi.fetchSerieDiaria).mockClear();

    fireEvent.change(screen.getByRole("combobox"), { target: { value: target } });

    await waitFor(() => {
      expect(vi.mocked(consumoApi.fetchSerieDiaria)).toHaveBeenCalledWith(
        TOKEN,
        SUMINISTRO,
        `${target}-01`,
        expect.stringMatching(new RegExp(`^${target}-\\d{2}$`)),
      );
    });
  });

  it("no vuelve a pedir el objetivo vigente al cambiar de mes", async () => {
    await renderListo();
    vi.mocked(objetivosApi.fetchObjetivo).mockClear();

    fireEvent.change(screen.getByRole("combobox"), { target: { value: mesAnterior() } });

    await waitFor(() => {
      expect(vi.mocked(consumoApi.fetchComparacion)).toHaveBeenCalled();
    });
    expect(vi.mocked(objetivosApi.fetchObjetivo)).not.toHaveBeenCalled();
  });
});

describe("ConsumoPage — card de total del mes filtrado", () => {
  it("muestra la card 'Mes actual' con el total del mes en curso", async () => {
    vi.mocked(consumoApi.fetchComparacion).mockResolvedValue({
      ...COMPARACION_VACIA,
      mes_actual: { mes: "2026-06-01", serie: [], total_kwh: 252.8 },
    });
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    expect(screen.getByText("Mes actual")).not.toBeNull();
    expect(screen.getByText(/252/)).not.toBeNull();
  });

  it("ya no muestra la card 'Últimos 7 días'", async () => {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    expect(screen.queryByText(/Últimos 7 días/i)).toBeNull();
  });

  it("al filtrar un mes pasado, el título deja de ser 'Mes actual'", async () => {
    render(<ConsumoPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByTestId("skeleton-block")).toBeNull());
    expect(screen.getByText("Mes actual")).not.toBeNull();

    const select = screen.getByRole("combobox") as HTMLSelectElement;
    const mesPasado = Array.from(select.options)[1].value;
    fireEvent.change(select, { target: { value: mesPasado } });

    await waitFor(() => expect(screen.queryByText("Mes actual")).toBeNull());
  });
});
