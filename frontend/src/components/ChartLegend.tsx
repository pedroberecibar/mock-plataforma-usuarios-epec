import { font, fontSize, fg } from "../design-tokens";

export interface ChartLegendItem {
  label: string;
  color: string;
  /** true → línea de referencia (swatch punteado); false/undefined → serie (swatch sólido). */
  dashed?: boolean;
}

/**
 * Leyenda inferior consistente para los gráficos de consumo.
 * Las series se muestran con un punto sólido; las líneas de referencia
 * (promedio, objetivo) con un trazo punteado, igual que en el gráfico.
 */
export function ChartLegend({ items }: { items: ChartLegendItem[] }) {
  if (items.length === 0) return null;
  return (
    <div style={{
      display:        "flex",
      flexWrap:       "wrap",
      justifyContent: "center",
      gap:            16,
      paddingTop:     8,
      fontFamily:     font.sans,
      fontSize:       fontSize.xs,
      color:          fg.secondary,
    }}>
      {items.map((it) => (
        <span key={it.label} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
          {it.dashed ? (
            <span style={{ width: 16, borderTop: `2px dashed ${it.color}` }} />
          ) : (
            <span style={{ width: 10, height: 10, borderRadius: "50%", background: it.color }} />
          )}
          {it.label}
        </span>
      ))}
    </div>
  );
}
