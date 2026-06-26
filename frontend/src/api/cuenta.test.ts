// @vitest-environment node
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchCuenta } from "./cuenta";

const mockFetch = vi.fn();
global.fetch = mockFetch;

const RESP = {
  personales: {
    nombre_o_razon_social: "Juana Pérez",
    tipo_documento: "DNI",
    nro_documento_masked: "****1815",
    cuit_masked: "********153",
    email: "juana@example.com",
  },
  suministro: {
    numero: "SRV-2817670",
    estado_servicio: "Activo",
    direccion: "Av. Siempre Viva 742",
    barrio: "Centro",
    localidad: "Córdoba",
    cp: "5000",
  },
  tarifa: {
    codigo: "140",
    descripcion: "1.a/f RESIDENCIAL",
    grupo_tarifario: "T1",
    clase: "1",
    clase_descripcion: "1 a-b-f Casas de familia",
    tension: "Baja",
  },
  medidor: {
    numero: "MED-99",
    marca: "CLOU",
    fase: "Monofásico",
    inteligente_desde: "2023-03-10",
  },
};

describe("fetchCuenta", () => {
  beforeEach(() => mockFetch.mockReset());

  it("hace GET /cuenta con el header Authorization", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, status: 200, json: async () => RESP });

    await fetchCuenta("mi-token");

    expect(mockFetch).toHaveBeenCalledWith(
      "/cuenta",
      { headers: { Authorization: "Bearer mi-token" } },
    );
  });

  it("retorna la respuesta parseada cuando es 200", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, status: 200, json: async () => RESP });
    const result = await fetchCuenta("tok");
    expect(result).toEqual(RESP);
  });

  it("lanza 'no_configurado' cuando el backend responde 503", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 503 });
    await expect(fetchCuenta("tok")).rejects.toThrow("no_configurado");
  });

  it("lanza 'sin_datos' cuando el backend responde 404", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 404 });
    await expect(fetchCuenta("tok")).rejects.toThrow("sin_datos");
  });

  it("lanza HTTP status en otros errores (ej. 401)", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 401 });
    await expect(fetchCuenta("bad")).rejects.toThrow("HTTP 401");
  });
});
