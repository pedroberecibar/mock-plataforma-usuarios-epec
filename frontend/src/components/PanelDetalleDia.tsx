import type { DetalleDiaResponse, PuntoSerieHoraria } from "../api/types";
import { GraficoConsumoHorario } from "./GraficoConsumoHorario";
import {
  bg,
  cardFeaturedStyle,
  fg,
  font,
  fontSize,
  fontWeight,
  labelStyle,
  radius,
  space,
} from "../design-tokens";

interface Props {
  fecha: string;
  detalle: DetalleDiaResponse | null;
  loading: boolean;
  onCerrar: () => void;
  serieHoraria?: PuntoSerieHoraria[];
}

function formatFechaLarga(fecha: string): string {
  const [y, m, d] = fecha.split("-");
  const meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  return `${parseInt(d)} ${meses[parseInt(m) - 1]} ${y}`;
}

export function PanelDetalleDia({ fecha, detalle, loading, onCerrar, serieHoraria }: Props) {
  const horaMaxima = serieHoraria && serieHoraria.length > 0
    ? serieHoraria.reduce((a, b) => (b.kwh > a.kwh ? b : a)).hora
    : undefined;

  return (
    <section
      data-testid="panel-detalle"
      style={{ ...cardFeaturedStyle, marginBottom: space[8] }}
    >
      <h3 style={{
        fontFamily:   font.sans,
        fontSize:     fontSize.sm,
        fontWeight:   fontWeight.semibold,
        color:        fg.link,
        margin:       `0 0 ${space[3]}px`,
        letterSpacing: "0.01em",
      }}>
        Detalle — {formatFechaLarga(fecha)}
      </h3>

      {loading && (
        <p style={{ fontFamily: font.sans, fontSize: fontSize.sm, color: fg.secondary, margin: 0 }}>
          Cargando detalle...
        </p>
      )}

      {!loading && detalle && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: space[3] }}>
          <DetalleCard
            label="Este día"
            valor={detalle.kwh_dia}
            testId="detalle-kwh-dia"
          />
          <DetalleCard
            label="Mismo día año anterior"
            valor={detalle.kwh_mismo_dia_anio_ant}
            testId="detalle-kwh-anio-ant"
          />
          <DetalleCard
            label={`Promedio zona (${detalle.n_vecinos} vec.)`}
            valor={detalle.kwh_promedio_zona}
            sinDatos={detalle.n_vecinos < 5}
            testId="detalle-kwh-zona"
          />
        </div>
      )}

      {serieHoraria && (
        <div style={{ marginTop: space[4] }}>
          <p style={labelStyle}>Consumo por hora</p>
          <GraficoConsumoHorario serie={serieHoraria} horaMaxima={horaMaxima} />
        </div>
      )}

      <button
        onClick={onCerrar}
        style={{
          marginTop:  space[3],
          background: "none",
          border:     "none",
          color:      fg.link,
          cursor:     "pointer",
          fontFamily: font.sans,
          fontSize:   fontSize.sm,
          fontWeight: fontWeight.medium,
          padding:    0,
        }}
      >
        Cerrar
      </button>
    </section>
  );
}

// ---------------------------------------------------------------------------

interface DetalleCardProps {
  label: string;
  valor: number | null;
  sinDatos?: boolean;
  testId?: string;
}

function DetalleCard({ label, valor, sinDatos, testId }: DetalleCardProps) {
  return (
    <div
      data-testid={testId}
      style={{
        background:   bg.surface,
        borderRadius: radius.sm,
        padding:      `${space[3]}px ${space[4]}px`,
        textAlign:    "center",
      }}
    >
      <div style={{
        fontFamily:    font.sans,
        fontSize:      fontSize.xs,
        fontWeight:    fontWeight.medium,
        color:         fg.secondary,
        marginBottom:  space[1],
        letterSpacing: "0.02em",
      }}>
        {label}
      </div>
      <div style={{
        fontFamily: font.technical,
        fontSize:   fontSize.lg,
        fontWeight: fontWeight.semibold,
        color:      fg.link,
      }}>
        {sinDatos
          ? "—"
          : valor !== null
            ? `${valor.toFixed(1)} kWh`
            : "Sin dato"}
      </div>
    </div>
  );
}
