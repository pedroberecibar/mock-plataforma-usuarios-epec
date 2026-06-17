import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PuntoSerie } from "../api/types";

interface Props {
  serie: PuntoSerie[];
}

function formatFecha(fecha: string): string {
  const [, , day] = fecha.split("-");
  return `${parseInt(day)}`;
}

export function GraficoConsumoDiario({ serie }: Props) {
  if (serie.length === 0) {
    return (
      <div style={{ padding: 24, textAlign: "center", color: "#9e9e9e" }}>
        Sin datos de consumo para el período seleccionado.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={serie} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e0e0e0" />
        <XAxis
          dataKey="fecha"
          tickFormatter={formatFecha}
          tick={{ fontSize: 11 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          unit=" kWh"
          tick={{ fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          width={64}
        />
        <Tooltip
          formatter={(value: number) => [`${value} kWh`, "Consumo"]}
          labelFormatter={(label: string) => `Fecha: ${label}`}
        />
        <Bar dataKey="kwh" fill="#2e7d32" radius={[3, 3, 0, 0]} maxBarSize={32} />
      </BarChart>
    </ResponsiveContainer>
  );
}
