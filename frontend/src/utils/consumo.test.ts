import { describe, expect, it } from "vitest";
import { agregarComparacionAnual, mesesDelAnio } from "./consumo";
import type { ComparacionResponse, ComparacionZonaResponse, PeriodoConsumo } from "../api/types";

describe("mesesDelAnio", () => {
  it("no incluye meses futuros del año en curso", () => {
    expect(mesesDelAnio(2026, new Date("2026-04-10T00:00:00"))).toEqual([
      "2026-01", "2026-02", "2026-03", "2026-04",
    ]);
  });

  it("incluye los 12 meses para un año pasado", () => {
    const r = mesesDelAnio(2025, new Date("2026-04-10T00:00:00"));
    expect(r).toHaveLength(12);
    expect(r[0]).toBe("2025-01");
    expect(r[11]).toBe("2025-12");
  });
});

function periodo(mes: string, total: number | null): PeriodoConsumo {
  return { mes, serie: [], total_kwh: total };
}

function zona(promedio: number | null, n: number): ComparacionZonaResponse {
  return { promedio_vecinos_kwh: promedio, n_vecinos: n, diferencia_pct: null, serie: [] };
}

function comp(mes: string, mio: number | null, zonaKwh: number | null, n: number): ComparacionResponse {
  return {
    mes_actual: periodo(`${mes}-01`, mio),
    mes_anterior: periodo("2000-01-01", null),
    mismo_mes_anio_anterior: periodo("2000-01-01", null),
    zona_mes_actual: zona(zonaKwh, n),
    datos_hasta: null,
  };
}

describe("agregarComparacionAnual", () => {
  it("suma mi consumo y el de la zona solo en meses con zona válida", () => {
    const r = agregarComparacionAnual([
      comp("2026-01", 100, 90, 6),
      comp("2026-02", 120, 110, 7),
      comp("2026-03", 80, null, 0), // sin zona → excluido del agregado
    ]);
    expect(r.totalMioKwh).toBe(220);   // 100 + 120
    expect(r.totalZonaKwh).toBe(200);  // 90 + 110
    expect(r.mesesConZona).toBe(2);
    expect(r.promedioMensualMioKwh).toBe(110);
    expect(r.promedioMensualZonaKwh).toBe(100);
    expect(r.diferenciaTotalPct).toBe(10); // (220-200)/200
  });

  it("descarta meses con menos de 5 vecinos", () => {
    const r = agregarComparacionAnual([
      comp("2026-01", 100, 90, 4), // pocos vecinos → no comparable
      comp("2026-02", 120, 110, 8),
    ]);
    expect(r.mesesConZona).toBe(1);
    expect(r.totalMioKwh).toBe(120);
    expect(r.totalZonaKwh).toBe(110);
  });

  it("devuelve nulls cuando no hay ningún mes comparable", () => {
    const r = agregarComparacionAnual([comp("2026-01", 100, null, 0)]);
    expect(r.totalMioKwh).toBeNull();
    expect(r.totalZonaKwh).toBeNull();
    expect(r.diferenciaTotalPct).toBeNull();
    expect(r.mesesConZona).toBe(0);
  });

  it("expone la serie mensual completa (incluye meses sin zona) y el máximo de vecinos", () => {
    const r = agregarComparacionAnual([
      comp("2026-01", 100, 90, 6),
      comp("2026-02", 80, null, 0),
    ]);
    expect(r.meses).toHaveLength(2);
    expect(r.meses[1]).toEqual({ mes: "2026-02", miKwh: 80, zonaKwh: null, nVecinos: 0 });
    expect(r.nVecinos).toBe(6);
  });
});
