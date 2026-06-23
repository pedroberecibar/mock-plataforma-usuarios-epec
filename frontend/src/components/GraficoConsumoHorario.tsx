import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PuntoSerieHoraria } from "../api/types";

interface Props {
  serie: PuntoSerieHoraria[];
  horaMaxima?: number;
}

function formatHora(hora: number): string {
  return `${hora}:00`;
}

function barColor(hora: number, horaMaxima?: number): string {
  if (hora === horaMaxima) return "#b22c2c";
  return "#1a6640";
}

// Completa las horas faltantes con 0 para que el gráfico tenga 24 barras siempre
function completar24horas(serie: PuntoSerieHoraria[]): PuntoSerieHoraria[] {
  const mapa = new Map(serie.map((p) => [p.hora, p.kwh]));
  return Array.from({ length: 24 }, (_, h) => ({
    hora: h,
    kwh: mapa.get(h) ?? 0,
  }));
}

export function GraficoConsumoHorario({ serie, horaMaxima }: Props) {
  if (serie.length === 0) {
    return (
      <div style={{ padding: 16, textAlign: "center", color: "#9e9e9e", fontSize: 13 }}>
        Sin datos horarios para esta fecha.
      </div>
    );
  }

  const datos = completar24horas(serie);

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart
        data={datos}
        margin={{ top: 4, right: 16, left: 0, bottom: 4 }}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e0e0e0" />
        <XAxis
          dataKey="hora"
          tickFormatter={(h: number) => h % 3 === 0 ? `${h}h` : ""}
          tick={{ fontSize: 10 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          unit=" kWh"
          tick={{ fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          width={56}
        />
        <Tooltip
          formatter={(value: number) => [`${value.toFixed(3)} kWh`, "Consumo"]}
          labelFormatter={(hora: number) => formatHora(hora)}
        />
        <Bar dataKey="kwh" radius={[2, 2, 0, 0]} maxBarSize={24}>
          {datos.map((punto) => (
            <Cell
              key={punto.hora}
              fill={barColor(punto.hora, horaMaxima)}
              opacity={punto.kwh === 0 ? 0.25 : 1}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
