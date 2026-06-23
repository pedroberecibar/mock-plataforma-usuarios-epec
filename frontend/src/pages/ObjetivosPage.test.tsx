import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import { ObjetivosPage } from "./ObjetivosPage";
import * as objetivosApi from "../api/objetivos";
import type { ObjetivoEstadoResponse } from "../api/types";

vi.mock("../api/objetivos");

const TOKEN = "tok";
const SUMINISTRO = "S001";

const OBJETIVO = { valor_kwh: 200, origen: "manual", vigente_desde: "2026-06-01" };

function makeEstado(overrides: Partial<ObjetivoEstadoResponse> = {}): ObjetivoEstadoResponse {
  return {
    objetivo_kwh: 200,
    promedio_vecinos_kwh: null,
    n_vecinos: 0,
    diferencia_pct: null,
    dias_transcurridos: 15,
    dias_objetivo_consumidos: 14,
    texto_dinamico: "en_ritmo",
    excedente_kwh: null,
    consumo_diario_real_kwh: 7,
    consumo_diario_objetivo_kwh: 6.67,
    ...overrides,
  };
}

beforeEach(() => {
  vi.mocked(objetivosApi.fetchObjetivo).mockResolvedValue(OBJETIVO);
  vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(makeEstado());
  vi.mocked(objetivosApi.evaluarObjetivo).mockResolvedValue(undefined);
});

describe("ObjetivosPage — barra de progreso (tests existentes)", () => {
  it("muestra la barra de progreso cuando hay objetivo y consumo", async () => {
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("progressbar")).not.toBeNull());
  });

  it("no muestra barra de progreso cuando no hay objetivo configurado", async () => {
    vi.mocked(objetivosApi.fetchObjetivo).mockResolvedValue(null);
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(makeEstado({ objetivo_kwh: null, texto_dinamico: "sin_objetivo" }));
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.queryByRole("progressbar")).toBeNull());
  });

  it("muestra advertencia cuando el consumo supera el 80% del objetivo", async () => {
    // consumoActual = 25 × 6.67 ≈ 166.7 kWh → pct = 0.83 → enAviso
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ dias_objetivo_consumidos: 25, texto_dinamico: "sobre_ritmo" })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("alert")).not.toBeNull());
  });

  it("muestra alerta de superado cuando el objetivo está agotado", async () => {
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({
        texto_dinamico: "agotado",
        excedente_kwh: 50,
        dias_objetivo_consumidos: 30,
      })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert.textContent).toMatch(/superado|objetivo alcanzado/i);
    });
  });
});

describe("ObjetivosPage — Indicador 2 (texto_dinamico)", () => {
  it("muestra 'Vas bien' cuando texto_dinamico=bajo_ritmo", async () => {
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ texto_dinamico: "bajo_ritmo", dias_objetivo_consumidos: 8 })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() =>
      expect(screen.getByTestId("indicador-2-texto").textContent).toMatch(/Vas bien/i)
    );
  });

  it("muestra 'en línea' cuando texto_dinamico=en_ritmo", async () => {
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ texto_dinamico: "en_ritmo" })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() =>
      expect(screen.getByTestId("indicador-2-texto").textContent).toMatch(/en línea/i)
    );
  });

  it("muestra advertencia cuando texto_dinamico=sobre_ritmo", async () => {
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ texto_dinamico: "sobre_ritmo", dias_objetivo_consumidos: 20 })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() =>
      expect(screen.getByTestId("indicador-2-texto").textContent).toMatch(/más rápido/i)
    );
  });

  it("muestra excedente cuando texto_dinamico=agotado", async () => {
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ texto_dinamico: "agotado", excedente_kwh: 40, dias_objetivo_consumidos: 30 })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => {
      const txt = screen.getByTestId("indicador-2-texto").textContent ?? "";
      expect(txt).toMatch(/alcanzaste/i);
      expect(txt).toMatch(/40/);
    });
  });
});

describe("ObjetivosPage — Indicador 1 (vs zona)", () => {
  it("muestra diferencia_pct positiva cuando el objetivo está por encima de la zona", async () => {
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ promedio_vecinos_kwh: 160, diferencia_pct: 25.0, n_vecinos: 6 })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() =>
      expect(screen.getByText(/\+25/)).not.toBeNull()
    );
  });

  it("muestra 'Sin datos suficientes' cuando promedio_vecinos_kwh es null", async () => {
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ promedio_vecinos_kwh: null, diferencia_pct: null, n_vecinos: 0 })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() =>
      expect(screen.getByText(/Sin datos suficientes/i)).not.toBeNull()
    );
  });
});

describe("ObjetivosPage — Trigger alerta", () => {
  it("llama a evaluarObjetivo al montar", async () => {
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() =>
      expect(vi.mocked(objetivosApi.evaluarObjetivo)).toHaveBeenCalledWith(TOKEN)
    );
  });
});

describe("ObjetivosPage — Design system (Etapa 6)", () => {
  it("renderiza PageHeader con título 'Objetivo de consumo'", async () => {
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("progressbar")).not.toBeNull());
    const banner = screen.getByRole("banner");
    expect(within(banner).getByText("Objetivo de consumo")).not.toBeNull();
  });

  it("muestra skeletons de carga en lugar de texto plano", () => {
    vi.mocked(objetivosApi.fetchObjetivo).mockReturnValue(new Promise(() => {}));
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    expect(screen.getAllByTestId("skeleton-block").length).toBeGreaterThan(0);
  });
});
