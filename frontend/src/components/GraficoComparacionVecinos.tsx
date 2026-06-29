import type { PuntoSerie } from "../api/types";
import { GraficoMiVsZona, type MiVsZonaPunto } from "./GraficoMiVsZona";

interface Props {
  serieMia: PuntoSerie[];
  serieZona: PuntoSerie[];
  objetivoDiarioKwh: number | null;
}

function formatDia(fecha: string): string {
  const [, , day] = fecha.split("-");
  return String(parseInt(day));
}

function formatFechaLarga(fecha: string): string {
  const d = new Date(fecha + "T00:00:00");
  const dias = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
  const meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  return `${dias[d.getDay()]} ${d.getDate()} ${meses[d.getMonth()]}`;
}

export function GraficoComparacionVecinos({ serieMia, serieZona, objetivoDiarioKwh }: Props) {
  if (serieMia.length === 0) return null;

  const zonaByFecha = new Map(serieZona.map((p) => [p.fecha, p.kwh]));
  const data: MiVsZonaPunto[] = serieMia.map((p) => ({
    x:            p.fecha,
    miConsumo:    p.kwh > 0 ? p.kwh : null,
    zonaPromedio: zonaByFecha.get(p.fecha) ?? null,
  }));

  return (
    <GraficoMiVsZona
      data={data}
      xTickFormatter={formatDia}
      tooltipTitle={formatFechaLarga}
      objetivo={objetivoDiarioKwh != null ? {
        valor: objetivoDiarioKwh,
        label: `Objetivo: ${objetivoDiarioKwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh/día`,
      } : null}
    />
  );
}
