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
import type { PuntoSerie } from "../api/types";

interface Props {
  serieMia: PuntoSerie[];
  serieZona: PuntoSerie[];
  objetivoDiarioKwh: number | null;
}

interface ChartPoint {
  fecha: string;
  miConsumo: number | null;
  zonaPromedio: number | null;
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

function CustomTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;

  const mio = payload.find((p) => p.dataKey === "miConsumo");
  const zona = payload.find((p) => p.dataKey === "zonaPromedio");

  return (
    <div
      style={{
        background: "#F3EDE2",
        border: "1px solid #D4C4A8",
        borderRadius: 8,
        padding: "10px 14px",
        fontFamily: font.sans,
        fontSize: fontSize.xs,
        boxShadow: "0 2px 8px rgba(100,80,60,0.12)",
      }}
    >
      <p style={{ margin: "0 0 6px", fontWeight: 600, color: fg.primary }}>
        {formatFechaLarga(label as string)}
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

export function GraficoComparacionVecinos({ serieMia, serieZona, objetivoDiarioKwh }: Props) {
  if (serieMia.length === 0) return null;

  const zonaByFecha = new Map(serieZona.map((p) => [p.fecha, p.kwh]));

  const data: ChartPoint[] = serieMia.map((p) => ({
    fecha: p.fecha,
    miConsumo: p.kwh > 0 ? p.kwh : null,
    zonaPromedio: zonaByFecha.get(p.fecha) ?? null,
  }));

  const tieneZona = serieZona.length > 0;

  return (
    <div style={{ marginTop: 20 }}>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={chartColor.grid} />
          <XAxis
            dataKey="fecha"
            tickFormatter={formatDia}
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

          {objetivoDiarioKwh != null && (
            <ReferenceLine
              y={objetivoDiarioKwh}
              stroke={color.warning}
              strokeWidth={1.5}
              strokeDasharray="6 3"
              label={{
                value: `Objetivo: ${objetivoDiarioKwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh/día`,
                position: "insideTopRight",
                fontSize: fontSize.xs,
                fill: color.warningDark,
                fontFamily: font.sans,
              }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
