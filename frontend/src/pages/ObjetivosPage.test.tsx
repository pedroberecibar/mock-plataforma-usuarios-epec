import { describe, expect, it, vi, beforeEach } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
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

describe("ObjetivosPage — card 'Tu objetivo vs. tu zona' eliminada", () => {
  it("ya no renderiza la card de comparación con la zona", async () => {
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ promedio_vecinos_kwh: 160, diferencia_pct: 25.0, n_vecinos: 6 })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("progressbar")).not.toBeNull());
    expect(screen.queryByText(/Tu objetivo vs\. tu zona/i)).toBeNull();
    expect(screen.queryByText(/Promedio zona/i)).toBeNull();
  });
});

describe("ObjetivosPage — días restantes + semáforo temporal", () => {
  // Hoy es 2026-06-29 → diasDelMesActual() = 30 (junio).
  it("muestra los días restantes del mes en ritmo y consumo acumulado", async () => {
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ dias_transcurridos: 20, dias_objetivo_consumidos: 18, consumo_acumulado_kwh: 120 })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    // 30 - 20 = 10 días restantes
    await waitFor(() =>
      expect(screen.getAllByText(/días restantes/i).length).toBeGreaterThan(0)
    );
    expect(screen.getAllByText("10").length).toBeGreaterThan(0);
  });

  it("NO marca alerta al consumir 98% del objetivo faltando 1 día (verde)", async () => {
    // objetivo 200; consumoActual = 29.4 × 6.67 ≈ 196 (98%); 1 día restante → ritmo ~1.01
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ dias_transcurridos: 29, dias_objetivo_consumidos: 29.4, texto_dinamico: "en_ritmo" })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("progressbar")).not.toBeNull());
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("marca alerta roja al consumir 98% del objetivo faltando 10 días", async () => {
    // objetivo 200; consumoActual = 29.4 × 6.67 ≈ 196 (98%); 20 días transcurridos → ritmo ~1.47
    vi.mocked(objetivosApi.fetchObjetivoEstado).mockResolvedValue(
      makeEstado({ dias_transcurridos: 20, dias_objetivo_consumidos: 29.4, texto_dinamico: "sobre_ritmo" })
    );
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => {
      const alert = screen.getByRole("alert");
      expect(alert.textContent).toMatch(/superado/i);
    });
  });
});

describe("ObjetivosPage — modal Modificar objetivo", () => {
  it("ya no muestra la card fija de edición; arranca con el modal cerrado", async () => {
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("button", { name: "Modificar" })).not.toBeNull());
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(screen.queryByLabelText("Objetivo en kWh")).toBeNull();
  });

  it("abre el modal con input y botones al hacer click en 'Modificar' del hero", async () => {
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("button", { name: "Modificar" })).not.toBeNull());

    fireEvent.click(screen.getByRole("button", { name: "Modificar" }));

    const dialog = screen.getByRole("dialog");
    expect(within(dialog).getByLabelText("Objetivo en kWh")).not.toBeNull();
    expect(within(dialog).getByRole("button", { name: "Guardar" })).not.toBeNull();
    expect(within(dialog).getByRole("button", { name: "Cancelar" })).not.toBeNull();
  });

  it("cierra el modal al hacer click en 'Cancelar'", async () => {
    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("button", { name: "Modificar" })).not.toBeNull());

    fireEvent.click(screen.getByRole("button", { name: "Modificar" }));
    fireEvent.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Cancelar" }));

    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
  });

  it("guarda el nuevo objetivo y cierra el modal", async () => {
    const nuevo = { valor_kwh: 250, origen: "manual", vigente_desde: "2026-06-29" };
    vi.mocked(objetivosApi.setObjetivo).mockResolvedValue(nuevo);

    render(<ObjetivosPage token={TOKEN} suministroId={SUMINISTRO} />);
    await waitFor(() => expect(screen.getByRole("button", { name: "Modificar" })).not.toBeNull());

    fireEvent.click(screen.getByRole("button", { name: "Modificar" }));
    const dialog = screen.getByRole("dialog");
    fireEvent.change(within(dialog).getByLabelText("Objetivo en kWh"), { target: { value: "250" } });
    fireEvent.click(within(dialog).getByRole("button", { name: "Guardar" }));

    await waitFor(() =>
      expect(vi.mocked(objetivosApi.setObjetivo)).toHaveBeenCalledWith(TOKEN, 250)
    );
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
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
