import type { ComparacionZonaResponse, PeriodoConsumo } from "../api/types";
import { bg, fg, color, font, fontSize, fontWeight, radius, shadow, space } from "../design-tokens";
import { GraficoComparacionVecinos } from "./GraficoComparacionVecinos";

interface Props {
  zona: ComparacionZonaResponse | null;
  mesActual: PeriodoConsumo;
  mismoMesAnioAnterior: PeriodoConsumo;
  objetivoDiarioKwh?: number | null;
}

interface DimensionCardProps {
  label: string;
  miValor: number | null;
  promedioVecinos: number | null;
  diferenciaPct: number | null;
  unidad: string;
}

function DimensionCard({ label, miValor, promedioVecinos, diferenciaPct, unidad }: DimensionCardProps) {
  const sube = diferenciaPct !== null && diferenciaPct > 0;
  const signo = diferenciaPct !== null && diferenciaPct > 0 ? "+" : "";
  const badgeColor = sube ? color.error : color.success;
  const badgeBg = sube ? color.errorLight : color.successLight;

  return (
    <div
      style={{
        flex:         1,
        minWidth:     200,
        padding:      `${space[4]}px ${space[5]}px`,
        borderRadius: `${radius.lg}px`,
        background:   bg.surface,
        boxShadow:    shadow.sm,
        fontFamily:   font.sans,
      }}
    >
      <p
        style={{
          margin: 0,
          marginBottom: space[3],
          fontSize: fontSize.xs,
          fontWeight: fontWeight.semibold,
          color: fg.secondary,
          textTransform: "uppercase" as const,
          letterSpacing: "0.06em",
          fontFamily: font.sans,
        }}
      >
        {label}
      </p>

      <div style={{ display: "flex", alignItems: "baseline", gap: space[2], marginBottom: space[2] }}>
        <span
          style={{
            fontFamily: font.technical,
            fontSize: fontSize["2xl"],
            fontWeight: fontWeight.bold,
            color: fg.primary,
            lineHeight: 1,
          }}
        >
          {miValor !== null ? miValor.toLocaleString("es-AR", { maximumFractionDigits: 1 }) : "—"}
        </span>
        <span style={{ fontFamily: font.sans, fontSize: fontSize.sm, color: fg.muted }}>
          {unidad}
        </span>
      </div>

      {promedioVecinos !== null && (
        <p
          style={{
            margin: 0,
            marginBottom: space[1],
            fontFamily: font.sans,
            fontSize: fontSize.sm,
            color: fg.secondary,
          }}
        >
          Zona:{" "}
          <strong style={{ color: fg.primary }}>
            {promedioVecinos.toLocaleString("es-AR", { maximumFractionDigits: 1 })} {unidad}
          </strong>
        </p>
      )}

      {diferenciaPct !== null && (
        <span
          style={{
            display: "inline-block",
            padding: `2px ${space[2]}px`,
            borderRadius: 4,
            background: badgeBg,
            color: badgeColor,
            fontSize: fontSize.xs,
            fontWeight: fontWeight.semibold,
            fontFamily: font.sans,
          }}
        >
          {signo}{diferenciaPct.toFixed(1)}% {sube ? "más que la zona" : "menos que la zona"}
        </span>
      )}

      {promedioVecinos === null && (
        <p style={{ margin: 0, fontFamily: font.sans, fontSize: fontSize.sm, color: fg.muted }}>
          Sin datos de zona
        </p>
      )}
    </div>
  );
}

export function PanelVecinosComparacion({ zona, mesActual, mismoMesAnioAnterior, objetivoDiarioKwh = null }: Props) {
  const tieneZona = zona !== null && zona.n_vecinos >= 5 && zona.promedio_vecinos_kwh !== null;

  const diasMesActual = mesActual.serie.length;
  const promedioDiarioMio =
    mesActual.total_kwh !== null && diasMesActual > 0
      ? mesActual.total_kwh / diasMesActual
      : null;
  const promedioDiarioZona =
    tieneZona && zona!.promedio_vecinos_kwh !== null && diasMesActual > 0
      ? zona!.promedio_vecinos_kwh / diasMesActual
      : null;
  const diferenciaDiariaPct =
    promedioDiarioMio !== null && promedioDiarioZona !== null && promedioDiarioZona > 0
      ? Math.round(((promedioDiarioMio - promedioDiarioZona) / promedioDiarioZona) * 1000) / 10
      : null;

  return (
    <section aria-label="comparación con vecinos">
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: space[4],
        }}
      >
        <h3
          style={{
            margin: 0,
            fontFamily: font.sans,
            fontSize: fontSize.base,
            fontWeight: fontWeight.semibold,
            color: fg.primary,
          }}
        >
          Comparación con vecinos
        </h3>
        {tieneZona && (
          <span
            style={{
              fontFamily: font.sans,
              fontSize: fontSize.xs,
              color: fg.muted,
            }}
          >
            {zona!.n_vecinos} vecinos en tu zona
          </span>
        )}
      </div>

      {!tieneZona && (
        <p
          style={{
            fontFamily: font.sans,
            fontSize: fontSize.sm,
            color: fg.muted,
            padding: `${space[4]}px`,
            background: bg.muted,
            borderRadius: 8,
            margin: 0,
          }}
        >
          Sin datos de vecinos disponibles por ahora. Los datos de tu zona se cargan automáticamente.
        </p>
      )}

      {tieneZona && (
        <>
          <div style={{ display: "flex", gap: space[4], flexWrap: "wrap" as const }}>
            <DimensionCard
              label="Total acumulado (este mes)"
              miValor={mesActual.total_kwh}
              promedioVecinos={zona!.promedio_vecinos_kwh}
              diferenciaPct={zona!.diferencia_pct}
              unidad="kWh"
            />
            <DimensionCard
              label="Promedio diario (este mes)"
              miValor={promedioDiarioMio}
              promedioVecinos={promedioDiarioZona}
              diferenciaPct={diferenciaDiariaPct}
              unidad="kWh/día"
            />
            {mismoMesAnioAnterior.total_kwh !== null && (
              <DimensionCard
                label="Mismo mes año anterior"
                miValor={mismoMesAnioAnterior.total_kwh}
                promedioVecinos={null}
                diferenciaPct={null}
                unidad="kWh"
              />
            )}
          </div>
          <GraficoComparacionVecinos
            serieMia={mesActual.serie}
            serieZona={zona!.serie}
            objetivoDiarioKwh={objetivoDiarioKwh}
          />
        </>
      )}
    </section>
  );
}
