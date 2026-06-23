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
import type { PuntoSerie } from "../api/types";
import { chartColor, fg } from "../design-tokens";

interface Props {
  serie: PuntoSerie[];
  onClickBarra?: (fecha: string) => void;
  maxFecha?: string;
  minFecha?: string;
}

function formatFecha(fecha: string): string {
  const [, , day] = fecha.split("-");
  return `${parseInt(day)}`;
}

function formatDiaSemana(fecha: string): string {
  const dias = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
  const d = new Date(fecha + "T00:00:00");
  return dias[d.getDay()];
}

function barColor(fecha: string, maxFecha?: string, minFecha?: string): string {
  if (fecha === maxFecha) return chartColor.anomaly;
  if (fecha === minFecha) return chartColor.primary;
  return chartColor.primary;
}

export function GraficoConsumoDiario({ serie, onClickBarra, maxFecha, minFecha }: Props) {
  if (serie.length === 0) {
    return (
      <div style={{ padding: 24, textAlign: "center", color: fg.muted }}>
        Sin datos de consumo para el período seleccionado.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart
        data={serie}
        margin={{ top: 4, right: 16, left: 0, bottom: 4 }}
        onClick={(payload) => {
          if (onClickBarra && payload?.activePayload?.[0]) {
            const punto = payload.activePayload[0].payload as PuntoSerie;
            onClickBarra(punto.fecha);
          }
        }}
        style={onClickBarra ? { cursor: "pointer" } : undefined}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={chartColor.grid} />
        <XAxis
          dataKey="fecha"
          tickFormatter={formatFecha}
          tick={{ fontSize: 11, fill: chartColor.axisText }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          unit=" kWh"
          tick={{ fontSize: 11, fill: chartColor.axisText }}
          tickLine={false}
          axisLine={false}
          width={64}
        />
        <Tooltip
          formatter={(value: number) => [`${value} kWh`, "Consumo"]}
          labelFormatter={(label: string) => `${formatDiaSemana(label)} ${label}`}
          contentStyle={{
            background:   chartColor.tooltipBg,
            border:       `1px solid ${chartColor.tooltipBorder}`,
            borderRadius: 8,
            fontSize:     13,
          }}
        />
        <Bar dataKey="kwh" radius={[3, 3, 0, 0]} maxBarSize={32}>
          {serie.map((punto) => (
            <Cell
              key={punto.fecha}
              fill={barColor(punto.fecha, maxFecha, minFecha)}
              opacity={punto.kwh === 0 ? 0.35 : punto.fecha === maxFecha ? 0.9 : 0.75}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
