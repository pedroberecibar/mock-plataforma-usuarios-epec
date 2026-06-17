// @vitest-environment node
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchComparacion, fetchSerieDiaria } from "./consumo";

const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("fetchSerieDiaria", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("construye la URL con suministro y rango de fechas", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ serie: [], datos_hasta: null }),
    });

    await fetchSerieDiaria("mi-token", "SRV-001", "2026-06-01", "2026-06-30");

    expect(mockFetch).toHaveBeenCalledWith(
      "/consumo/SRV-001/diario?desde=2026-06-01&hasta=2026-06-30",
      { headers: { Authorization: "Bearer mi-token" } },
    );
  });

  it("retorna la respuesta parseada cuando la respuesta es ok", async () => {
    const respuesta = {
      serie: [{ fecha: "2026-06-01", kwh: 12.5 }],
      datos_hasta: "2026-06-15",
    };
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => respuesta });

    const result = await fetchSerieDiaria("tok", "SRV-001", "2026-06-01", "2026-06-30");

    expect(result).toEqual(respuesta);
  });

  it("lanza error con HTTP status cuando la respuesta no es ok", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 401 });

    await expect(
      fetchSerieDiaria("bad", "SRV-001", "2026-06-01", "2026-06-30"),
    ).rejects.toThrow("HTTP 401");
  });
});

describe("fetchComparacion", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("construye la URL con suministro y mes", async () => {
    const stub = {
      mes_actual: { mes: "2026-06-01", serie: [], total_kwh: null },
      mes_anterior: { mes: "2026-05-01", serie: [], total_kwh: null },
      mismo_mes_anio_anterior: { mes: "2025-06-01", serie: [], total_kwh: null },
      datos_hasta: null,
    };
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => stub });

    await fetchComparacion("token", "SRV-001", "2026-06");

    expect(mockFetch).toHaveBeenCalledWith(
      "/consumo/SRV-001/comparacion?mes=2026-06",
      { headers: { Authorization: "Bearer token" } },
    );
  });

  it("lanza error con HTTP status en respuesta no-ok", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 404 });

    await expect(fetchComparacion("tok", "SRV-X", "2026-06")).rejects.toThrow("HTTP 404");
  });
});
