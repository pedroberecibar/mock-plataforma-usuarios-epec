// @vitest-environment node
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchHome } from "./home";

const mockFetch = vi.fn();
global.fetch = mockFetch;

const stubHome = {
  consumo_mes: { total_kwh: 120.5, vs_mes_anterior_pct: -5.2, vs_anio_anterior_pct: 10.0 },
  comparacion_zona: { promedio_vecinos_kwh: 100.0, n_vecinos: 3, diferencia_pct: 20.5 },
  proyeccion: {
    mes: "2026-06-01",
    metodo_aplicado: "reciente",
    bandera_confianza: "baja",
    rango_inferior_kwh: 90.0,
    rango_superior_kwh: 135.0,
  },
  datos_hasta: "2026-06-17",
  timestamp: "2026-06-17T12:00:00Z",
};

describe("fetchHome", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("construye la URL con suministro y mes", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => stubHome });

    await fetchHome("mi-token", "SRV-001", "2026-06");

    expect(mockFetch).toHaveBeenCalledWith("/home/SRV-001?mes=2026-06", {
      headers: { Authorization: "Bearer mi-token" },
    });
  });

  it("retorna la respuesta parseada cuando la respuesta es ok", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => stubHome });

    const result = await fetchHome("tok", "SRV-001", "2026-06");

    expect(result.consumo_mes.total_kwh).toBe(120.5);
    expect(result.proyeccion.metodo_aplicado).toBe("reciente");
    expect(result.comparacion_zona.n_vecinos).toBe(3);
  });

  it("lanza error con HTTP status cuando la respuesta no es ok", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 401 });

    await expect(fetchHome("bad", "SRV-001", "2026-06")).rejects.toThrow("HTTP 401");
  });

  it("lanza error HTTP 404 cuando el suministro no existe", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 404 });

    await expect(fetchHome("tok", "SRV-X", "2026-06")).rejects.toThrow("HTTP 404");
  });
});
