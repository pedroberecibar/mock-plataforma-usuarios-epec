import { describe, expect, it } from "vitest";
import {
  diasHastaVencimiento,
  formatImporte,
  proximoVencimiento,
  textoDiasRestantes,
} from "./factura";
import type { FacturaDocumento } from "../api/types";

const HOY = new Date("2026-06-30T10:00:00");

function doc(over: Partial<FacturaDocumento>): FacturaDocumento {
  return {
    periodo: "06/2026",
    importe: 1000,
    fecha_vencimiento: "2026-07-05",
    estado: null,
    url_pdf: null,
    ...over,
  };
}

describe("diasHastaVencimiento", () => {
  it("cuenta los días hasta un vencimiento futuro", () => {
    expect(diasHastaVencimiento("2026-07-05", HOY)).toBe(5);
  });

  it("devuelve negativo cuando ya venció", () => {
    expect(diasHastaVencimiento("2026-06-28", HOY)).toBe(-2);
  });

  it("devuelve 0 cuando vence hoy", () => {
    expect(diasHastaVencimiento("2026-06-30", HOY)).toBe(0);
  });
});

describe("proximoVencimiento", () => {
  it("elige el documento con el vencimiento más próximo", () => {
    const docs = [
      doc({ fecha_vencimiento: "2026-07-20" }),
      doc({ fecha_vencimiento: "2026-07-03" }),
    ];
    expect(proximoVencimiento(docs, HOY)?.fecha_vencimiento).toBe("2026-07-03");
  });

  it("devuelve null cuando ningún documento tiene fecha", () => {
    expect(proximoVencimiento([doc({ fecha_vencimiento: null })], HOY)).toBeNull();
  });

  it("devuelve null con lista vacía", () => {
    expect(proximoVencimiento([], HOY)).toBeNull();
  });
});

describe("textoDiasRestantes", () => {
  it("describe vencida, hoy, mañana y futuro", () => {
    expect(textoDiasRestantes(-1)).toBe("Vencida");
    expect(textoDiasRestantes(0)).toBe("Vence hoy");
    expect(textoDiasRestantes(1)).toBe("Vence mañana");
    expect(textoDiasRestantes(4)).toBe("Faltan 4 días");
  });
});

describe("formatImporte", () => {
  it("formatea con separador de miles argentino", () => {
    expect(formatImporte(18420.5)).toMatch(/18\.420/);
  });
});
