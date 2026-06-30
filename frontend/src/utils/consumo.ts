import type { ComparacionResponse } from "../api/types";

export interface MesTotal {
  mes: string; // "YYYY-MM"
  kwh: number;
}

/** Lista de meses "YYYY-MM" del año pedido, sin meses futuros si es el año en curso. */
export function mesesDelAnio(anio: number, hoy: Date = new Date()): string[] {
  const ultimoMes = anio === hoy.getFullYear() ? hoy.getMonth() + 1 : 12;
  const meses: string[] = [];
  for (let m = 1; m <= ultimoMes; m++) {
    meses.push(`${anio}-${String(m).padStart(2, "0")}`);
  }
  return meses;
}

/** Día-del-mes (1..31) de una fecha "YYYY-MM-DD". */
function diaDelMes(fecha: string): number {
  return parseInt(fecha.slice(8, 10), 10);
}

/**
 * Total de `serieComparacion` restringido a los mismos días calendario que
 * tienen dato en `serieActual` (comparación a igual período). Espeja el helper
 * de backend `domain.comparacion_periodo.total_en_dias`.
 */
export function totalEnMismosDias(
  serieComparacion: { fecha: string; kwh: number }[],
  serieActual: { fecha: string; kwh: number }[],
): number {
  const dias = new Set(serieActual.map((p) => diaDelMes(p.fecha)));
  return serieComparacion
    .filter((p) => dias.has(diaDelMes(p.fecha)))
    .reduce((s, p) => s + p.kwh, 0);
}

// ---------------------------------------------------------------------------
// Comparación anual con vecinos — agregada a partir de las comparaciones
// mensuales (el backend solo expone zona a nivel mensual).
// ---------------------------------------------------------------------------
const MIN_VECINOS = 5;

export interface MesVsZona {
  mes: string; // "YYYY-MM"
  miKwh: number | null;
  zonaKwh: number | null;
  nVecinos: number;
}

export interface ComparacionAnual {
  meses: MesVsZona[];
  totalMioKwh: number | null;
  totalZonaKwh: number | null;
  diferenciaTotalPct: number | null;
  promedioMensualMioKwh: number | null;
  promedioMensualZonaKwh: number | null;
  diferenciaPromedioPct: number | null;
  nVecinos: number;
  mesesConZona: number;
}

function round1(x: number): number {
  return Math.round(x * 10) / 10;
}

function pct(mio: number | null, zona: number | null): number | null {
  if (mio === null || zona === null || zona === 0) return null;
  return round1(((mio - zona) / zona) * 100);
}

export function agregarComparacionAnual(comparaciones: ComparacionResponse[]): ComparacionAnual {
  const meses: MesVsZona[] = comparaciones.map((c) => {
    const zona = c.zona_mes_actual;
    const zonaValida =
      zona != null && zona.n_vecinos >= MIN_VECINOS && zona.promedio_vecinos_kwh !== null;
    return {
      mes: c.mes_actual.mes.slice(0, 7),
      miKwh: c.mes_actual.total_kwh,
      zonaKwh: zonaValida ? zona!.promedio_vecinos_kwh : null,
      nVecinos: zona?.n_vecinos ?? 0,
    };
  });

  // Para una comparación justa, agregamos solo meses con zona válida y consumo propio.
  const comparables = meses.filter((m) => m.zonaKwh !== null && m.miKwh !== null);
  const mesesConZona = comparables.length;
  const sum = (arr: number[]) => arr.reduce((a, b) => a + b, 0);

  const totalMioKwh = mesesConZona ? round1(sum(comparables.map((m) => m.miKwh!))) : null;
  const totalZonaKwh = mesesConZona ? round1(sum(comparables.map((m) => m.zonaKwh!))) : null;
  const promedioMensualMioKwh = totalMioKwh !== null ? round1(totalMioKwh / mesesConZona) : null;
  const promedioMensualZonaKwh = totalZonaKwh !== null ? round1(totalZonaKwh / mesesConZona) : null;
  const nVecinos = meses.reduce((max, m) => Math.max(max, m.nVecinos), 0);

  return {
    meses,
    totalMioKwh,
    totalZonaKwh,
    diferenciaTotalPct: pct(totalMioKwh, totalZonaKwh),
    promedioMensualMioKwh,
    promedioMensualZonaKwh,
    diferenciaPromedioPct: pct(promedioMensualMioKwh, promedioMensualZonaKwh),
    nVecinos,
    mesesConZona,
  };
}
