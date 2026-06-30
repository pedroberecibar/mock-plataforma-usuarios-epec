import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MesTotal } from "../utils/consumo";
import { chartColor, fg } from "../design-tokens";
import { ChartLegend } from "./ChartLegend";

interface Props {
  serie: MesTotal[];
  onClickMes?: (mes: string) => void;
  mesDestacado?: string; // "YYYY-MM" a resaltar (ej. mes actual)
  /** Promedio del período (kWh/mes) — se dibuja como línea de referencia. */
  promedio?: number | null;
}

const MESES_CORTOS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

function nombreMesCorto(mes: string): string {
  const m = parseInt(mes.split("-")[1], 10);
  return MESES_CORTOS[m - 1] ?? mes;
}

function nombreMesLargo(mes: string): string {
  const [y, m] = mes.split("-").map(Number);
  const raw = new Date(y, m - 1, 1).toLocaleDateString("es-AR", { month: "long", year: "numeric" });
  return raw.charAt(0).toUpperCase() + raw.slice(1);
}

export function GraficoConsumoMensual({ serie, onClickMes, mesDestacado, promedio }: Props) {
  if (serie.length === 0) {
    return (
      <div style={{ padding: 24, textAlign: "center", color: fg.muted }}>
        Sin datos de consumo para el año seleccionado.
      </div>
    );
  }

  const promedioLabel =
    promedio != null && promedio > 0
      ? `Promedio: ${promedio.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`
      : null;

  return (
    <>
    <ResponsiveContainer width="100%" height={260}>
      <BarChart
        data={serie}
        margin={{ top: 4, right: 16, left: 0, bottom: 4 }}
        onClick={(payload) => {
          if (onClickMes && payload?.activePayload?.[0]) {
            const punto = payload.activePayload[0].payload as MesTotal;
            onClickMes(punto.mes);
          }
        }}
        style={onClickMes ? { cursor: "pointer" } : undefined}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={chartColor.grid} />
        <XAxis
          dataKey="mes"
          tickFormatter={nombreMesCorto}
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
          labelFormatter={(label: string) => nombreMesLargo(label)}
          contentStyle={{
            background:   chartColor.tooltipBg,
            border:       `1px solid ${chartColor.tooltipBorder}`,
            borderRadius: 8,
            fontSize:     13,
          }}
        />
        <Bar dataKey="kwh" radius={[3, 3, 0, 0]} maxBarSize={40}>
          {serie.map((punto) => (
            <Cell
              key={punto.mes}
              fill={chartColor.primary}
              opacity={punto.kwh === 0 ? 0.25 : punto.mes === mesDestacado ? 0.95 : 0.7}
            />
          ))}
        </Bar>
        {promedioLabel != null && (
          <ReferenceLine
            y={promedio!}
            stroke={chartColor.axisText}
            strokeWidth={1.5}
            strokeDasharray="6 3"
          />
        )}
      </BarChart>
    </ResponsiveContainer>
    {promedioLabel != null && (
      <ChartLegend items={[{ label: promedioLabel, color: chartColor.axisText, dashed: true }]} />
    )}
    </>
  );
}
