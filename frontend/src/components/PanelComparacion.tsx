import type { PeriodoConsumo } from "../api/types";

interface Props {
  mesActual: PeriodoConsumo;
  mesAnterior: PeriodoConsumo;
  mismoMesAnioAnterior: PeriodoConsumo;
}

function formatMes(fecha: string): string {
  const [year, month] = fecha.split("-");
  const d = new Date(parseInt(year), parseInt(month) - 1, 1);
  return d.toLocaleDateString("es-AR", { month: "long", year: "numeric" });
}

function TarjetaPeriodo({
  periodo,
  etiqueta,
}: {
  periodo: PeriodoConsumo;
  etiqueta: string;
}) {
  return (
    <div
      style={{
        flex: 1,
        padding: "16px 20px",
        borderRadius: 8,
        background: "#f5f5f5",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 12, color: "#757575", marginBottom: 4 }}>{etiqueta}</div>
      <div style={{ fontSize: 11, color: "#9e9e9e", marginBottom: 8 }}>
        {formatMes(periodo.mes)}
      </div>
      {periodo.total_kwh !== null ? (
        <div style={{ fontSize: 28, fontWeight: 700, color: "#1b5e20" }}>
          {periodo.total_kwh.toFixed(1)}
          <span style={{ fontSize: 14, fontWeight: 400, color: "#555", marginLeft: 4 }}>kWh</span>
        </div>
      ) : (
        <div style={{ fontSize: 14, color: "#bdbdbd" }}>Sin datos</div>
      )}
    </div>
  );
}

export function PanelComparacion({ mesActual, mesAnterior, mismoMesAnioAnterior }: Props) {
  return (
    <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
      <TarjetaPeriodo periodo={mesActual} etiqueta="Este mes" />
      <TarjetaPeriodo periodo={mesAnterior} etiqueta="Mes anterior" />
      <TarjetaPeriodo periodo={mismoMesAnioAnterior} etiqueta="Mismo mes año anterior" />
    </div>
  );
}
