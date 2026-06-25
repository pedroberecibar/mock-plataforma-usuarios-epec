import { describe, expect, it } from "vitest";
import { primerDiaDeMes, ultimoDiaDeMes, ultimoDiaConDatos, listaMeses } from "./meses";

describe("helpers de meses", () => {
  it("primerDiaDeMes devuelve el día 01 del mes", () => {
    expect(primerDiaDeMes("2026-04")).toBe("2026-04-01");
  });

  it("ultimoDiaDeMes devuelve el último día calendario del mes", () => {
    expect(ultimoDiaDeMes("2026-04")).toBe("2026-04-30");
    expect(ultimoDiaDeMes("2026-02")).toBe("2026-02-28");
    expect(ultimoDiaDeMes("2024-02")).toBe("2024-02-29"); // bisiesto
  });

  it("ultimoDiaConDatos usa hoy cuando el mes es el actual", () => {
    expect(ultimoDiaConDatos("2026-06", "2026-06-17")).toBe("2026-06-17");
  });

  it("ultimoDiaConDatos usa fin de mes cuando el mes es pasado", () => {
    expect(ultimoDiaConDatos("2026-04", "2026-06-17")).toBe("2026-04-30");
  });

  it("listaMeses devuelve N meses hacia atrás, empezando por el actual", () => {
    const hoy = new Date(2026, 5, 17); // junio 2026 (mes index 5)
    const meses = listaMeses(12, hoy);
    expect(meses).toHaveLength(12);
    expect(meses[0].value).toBe("2026-06");
    expect(meses[1].value).toBe("2026-05");
    expect(meses[11].value).toBe("2025-07");
  });

  it("listaMeses no incluye meses futuros", () => {
    const hoy = new Date(2026, 5, 17);
    const meses = listaMeses(12, hoy);
    expect(meses.every((m) => m.value <= "2026-06")).toBe(true);
  });

  it("listaMeses capitaliza la etiqueta en es-AR", () => {
    const hoy = new Date(2026, 5, 17);
    const [actual] = listaMeses(1, hoy);
    expect(actual.label).toMatch(/^Junio de 2026$/);
  });
});
