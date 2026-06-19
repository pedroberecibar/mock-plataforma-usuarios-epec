import type { TooltipProps } from "recharts";
import { chartTheme } from "./ChartTheme";

export function WarmTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background:   chartTheme.tooltipBg,
      border:       `1px solid ${chartTheme.tooltipBorder}`,
      borderRadius: chartTheme.tooltipRadius,
      padding:      "10px 14px",
      fontFamily:   "'Inter', sans-serif",
      boxShadow:    "0 4px 12px rgba(100,80,60,0.12)",
    }}>
      <p style={{ color: chartTheme.tooltipTextSecondary, fontSize: 11, margin: "0 0 4px" }}>
        {label}
      </p>
      {payload.map(entry => (
        <p key={entry.name} style={{
          color:      chartTheme.tooltipTextPrimary,
          fontSize:   16,
          fontWeight: 500,
          margin:     0,
          fontFamily: "'Space Grotesk', sans-serif",
        }}>
          {entry.value?.toLocaleString("es-AR")} kWh
        </p>
      ))}
    </div>
  );
}
