import type { ComparacionAnual } from "../utils/consumo";
import { bg, fg, font, fontSize, fontWeight, space } from "../design-tokens";
import { DimensionCard } from "./PanelVecinosComparacion";
import { GraficoMiVsZona, type MiVsZonaPunto } from "./GraficoMiVsZona";

interface Props {
  comparacion: ComparacionAnual | null;
  anio: number;
}

const MESES_CORTOS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

function mesCorto(mes: string): string {
  return MESES_CORTOS[parseInt(mes.split("-")[1], 10) - 1] ?? mes;
}

function mesLargo(mes: string): string {
  const [y, m] = mes.split("-").map(Number);
  const raw = new Date(y, m - 1, 1).toLocaleDateString("es-AR", { month: "long", year: "numeric" });
  return raw.charAt(0).toUpperCase() + raw.slice(1);
}

export function PanelVecinosAnual({ comparacion, anio }: Props) {
  const tieneDatos = comparacion != null && comparacion.mesesConZona > 0;

  const data: MiVsZonaPunto[] =
    comparacion?.meses.map((m) => ({ x: m.mes, miConsumo: m.miKwh, zonaPromedio: m.zonaKwh })) ?? [];

  return (
    <section aria-label="comparación con vecinos anual">
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: space[4] }}>
        <h3 style={{
          margin:     0,
          fontFamily: font.sans,
          fontSize:   fontSize.base,
          fontWeight: fontWeight.semibold,
          color:      fg.primary,
        }}>
          Comparación con vecinos · {anio}
        </h3>
        {tieneDatos && (
          <span style={{ fontFamily: font.sans, fontSize: fontSize.xs, color: fg.muted }}>
            {comparacion!.nVecinos} vecinos en tu zona
          </span>
        )}
      </div>

      {!tieneDatos ? (
        <p style={{
          fontFamily:   font.sans,
          fontSize:     fontSize.sm,
          color:        fg.muted,
          padding:      `${space[4]}px`,
          background:   bg.muted,
          borderRadius: 8,
          margin:       0,
        }}>
          {comparacion === null
            ? "Cargando comparación anual…"
            : "Sin datos de vecinos suficientes para este año."}
        </p>
      ) : (
        <>
          <div style={{ display: "flex", gap: space[4], flexWrap: "wrap" as const }}>
            <DimensionCard
              label={`Total del año · ${anio}`}
              miValor={comparacion!.totalMioKwh}
              promedioVecinos={comparacion!.totalZonaKwh}
              diferenciaPct={comparacion!.diferenciaTotalPct}
              unidad="kWh"
            />
            <DimensionCard
              label="Promedio mensual"
              miValor={comparacion!.promedioMensualMioKwh}
              promedioVecinos={comparacion!.promedioMensualZonaKwh}
              diferenciaPct={comparacion!.diferenciaPromedioPct}
              unidad="kWh/mes"
            />
          </div>
          <GraficoMiVsZona data={data} xTickFormatter={mesCorto} tooltipTitle={mesLargo} />
        </>
      )}
    </section>
  );
}
