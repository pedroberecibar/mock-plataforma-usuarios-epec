import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TooltipProps } from "recharts";
import { chartColor, color, fg, font, fontSize } from "../design-tokens";

export interface MiVsZonaPunto {
  x: string; // clave del eje X (fecha "YYYY-MM-DD" o mes "YYYY-MM")
  miConsumo: number | null;
  zonaPromedio: number | null;
}

interface Props {
  data: MiVsZonaPunto[];
  xTickFormatter: (x: string) => string;
  tooltipTitle: (x: string) => string;
  objetivo?: { valor: number; label: string } | null;
  height?: number;
}

/**
 * Gráfico genérico "mi consumo (barras) vs promedio de la zona (línea)".
 * Reutilizado por la comparación diaria (mes) y mensual (año).
 */
export function GraficoMiVsZona({ data, xTickFormatter, tooltipTitle, objetivo = null, height = 280 }: Props) {
  if (data.length === 0) return null;
  const tieneZona = data.some((p) => p.zonaPromedio !== null);

  function CustomTooltip({ active, payload, label }: TooltipProps<number, string>) {
    if (!active || !payload?.length) return null;
    const mio = payload.find((p) => p.dataKey === "miConsumo");
    const zona = payload.find((p) => p.dataKey === "zonaPromedio");
    return (
      <div style={{
        background:   chartColor.tooltipBg,
        border:       `1px solid ${chartColor.tooltipBorder}`,
        borderRadius: 8,
        padding:      "10px 14px",
        fontFamily:   font.sans,
        fontSize:     fontSize.xs,
        boxShadow:    "0 2px 8px rgba(100,80,60,0.12)",
      }}>
        <p style={{ margin: "0 0 6px", fontWeight: 600, color: fg.primary }}>
          {tooltipTitle(label as string)}
        </p>
        {mio?.value != null && (
          <p style={{ margin: "2px 0", color: chartColor.primary }}>
            <span style={{ fontWeight: 600 }}>{mio.value.toLocaleString("es-AR", { maximumFractionDigits: 1 })}</span>
            {" kWh — Mi consumo"}
          </p>
        )}
        {zona?.value != null && (
          <p style={{ margin: "2px 0", color: color.info }}>
            <span style={{ fontWeight: 600 }}>{zona.value.toLocaleString("es-AR", { maximumFractionDigits: 1 })}</span>
            {" kWh — Promedio zona"}
          </p>
        )}
      </div>
    );
  }

  return (
    <div style={{ marginTop: 20 }}>
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={chartColor.grid} />
          <XAxis
            dataKey="x"
            tickFormatter={xTickFormatter}
            tick={{ fontSize: fontSize.xs, fill: chartColor.axisText, fontFamily: font.sans }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            unit=" kWh"
            tick={{ fontSize: fontSize.xs, fill: chartColor.axisText, fontFamily: font.sans }}
            tickLine={false}
            axisLine={false}
            width={68}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontFamily: font.sans, fontSize: fontSize.xs, paddingTop: 8 }}
          />

          <Bar
            dataKey="miConsumo"
            name="Mi consumo"
            fill={chartColor.primary}
            radius={[3, 3, 0, 0]}
            maxBarSize={28}
            opacity={0.85}
          />

          {tieneZona && (
            <Line
              dataKey="zonaPromedio"
              name="Promedio vecinos"
              type="monotone"
              stroke={color.info}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: color.info }}
              connectNulls
            />
          )}

          {objetivo != null && (
            <ReferenceLine
              y={objetivo.valor}
              stroke={color.warning}
              strokeWidth={1.5}
              strokeDasharray="6 3"
              label={{
                value:      objetivo.label,
                position:   "insideTopRight",
                fontSize:   fontSize.xs,
                fill:       color.warningDark,
                fontFamily: font.sans,
              }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
