import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { OnboardingObjetivoPage } from "./OnboardingObjetivoPage";
import * as objetivosApi from "../api/objetivos";
import type { ObjetivoSugeridoResponse } from "../api/types";

vi.mock("../api/objetivos");

const TOKEN = "tok";
const SUMINISTRO = "S001";
const OBJETIVO_GUARDADO = { valor_kwh: 200, origen: "sugerido", vigente_desde: "2026-06-01" };

const SUGERIDO_CON_DATOS: ObjetivoSugeridoResponse = {
  valor_kwh: 200,
  n_vecinos: 5,
  sin_datos: false,
};

const SUGERIDO_SIN_DATOS: ObjetivoSugeridoResponse = {
  valor_kwh: null,
  n_vecinos: 3,
  sin_datos: true,
};

beforeEach(() => {
  vi.mocked(objetivosApi.fetchObjetivoSugerido).mockResolvedValue(SUGERIDO_CON_DATOS);
  vi.mocked(objetivosApi.setObjetivo).mockResolvedValue(OBJETIVO_GUARDADO);
});

describe("OnboardingObjetivoPage", () => {
  it("muestra el objetivo sugerido cuando hay datos", async () => {
    render(
      <OnboardingObjetivoPage
        token={TOKEN}
        suministroId={SUMINISTRO}
        onObjetivoGuardado={vi.fn()}
      />
    );
    await waitFor(() => expect(screen.getByText(/200/)).not.toBeNull());
  });

  it("muestra mensaje sin datos cuando sin_datos=true", async () => {
    vi.mocked(objetivosApi.fetchObjetivoSugerido).mockResolvedValue(SUGERIDO_SIN_DATOS);
    render(
      <OnboardingObjetivoPage
        token={TOKEN}
        suministroId={SUMINISTRO}
        onObjetivoGuardado={vi.fn()}
      />
    );
    await waitFor(() =>
      expect(screen.getByText(/Sin datos suficientes/i)).not.toBeNull()
    );
  });

  it("llama a setObjetivo con el valor sugerido al hacer click en 'Usar este objetivo'", async () => {
    const onGuardado = vi.fn();
    render(
      <OnboardingObjetivoPage
        token={TOKEN}
        suministroId={SUMINISTRO}
        onObjetivoGuardado={onGuardado}
      />
    );
    const btn = await screen.findByText(/Usar este objetivo/i);
    fireEvent.click(btn);
    await waitFor(() => {
      expect(vi.mocked(objetivosApi.setObjetivo)).toHaveBeenCalledWith(TOKEN, 200);
      expect(onGuardado).toHaveBeenCalledWith(OBJETIVO_GUARDADO);
    });
  });

  it("muestra input manual al hacer click en 'Ingresar mi objetivo'", async () => {
    render(
      <OnboardingObjetivoPage
        token={TOKEN}
        suministroId={SUMINISTRO}
        onObjetivoGuardado={vi.fn()}
      />
    );
    const btn = await screen.findByText(/Ingresar mi objetivo/i);
    fireEvent.click(btn);
    await waitFor(() =>
      expect(screen.getByRole("spinbutton", { name: /Objetivo en kWh/i })).not.toBeNull()
    );
  });

  it("guarda el objetivo manual correctamente", async () => {
    const onGuardado = vi.fn();
    render(
      <OnboardingObjetivoPage
        token={TOKEN}
        suministroId={SUMINISTRO}
        onObjetivoGuardado={onGuardado}
      />
    );
    fireEvent.click(await screen.findByText(/Ingresar mi objetivo/i));
    const input = screen.getByRole("spinbutton", { name: /Objetivo en kWh/i });
    fireEvent.change(input, { target: { value: "180" } });
    fireEvent.click(screen.getByText("Guardar"));
    await waitFor(() => {
      expect(vi.mocked(objetivosApi.setObjetivo)).toHaveBeenCalledWith(TOKEN, 180);
      expect(onGuardado).toHaveBeenCalled();
    });
  });
});
