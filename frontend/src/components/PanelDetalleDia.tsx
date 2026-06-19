import type { DetalleDiaResponse } from "../api/types";

interface Props {
  fecha: string;
  detalle: DetalleDiaResponse | null;
  loading: boolean;
  onCerrar: () => void;
}

function formatFechaLarga(fecha: string): string {
  const [y, m, d] = fecha.split("-");
  const meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  return `${parseInt(d)} ${meses[parseInt(m) - 1]} ${y}`;
}

export function PanelDetalleDia({ fecha, detalle, loading, onCerrar }: Props) {
  return (
    <section
      data-testid="panel-detalle"
      style={{
        marginBottom: 32,
        background: "#f9fbe7",
        border: "1px solid #c5e1a5",
        borderRadius: 8,
        padding: "16px 20px",
      }}
    >
      <h3 style={{ fontSize: 15, color: "#33691e", margin: "0 0 12px" }}>
        Detalle — {formatFechaLarga(fecha)}
      </h3>

      {loading && <p style={{ color: "#555", margin: 0 }}>Cargando detalle...</p>}

      {!loading && detalle && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
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

      <button
        onClick={onCerrar}
        style={{
          marginTop: 12,
          background: "none",
          border: "none",
          color: "#558b2f",
          cursor: "pointer",
          fontSize: 13,
          padding: 0,
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
        background: "#fff",
        border: "1px solid #dcedc8",
        borderRadius: 6,
        padding: "12px 14px",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 600, color: "#2e7d32" }}>
        {sinDatos
          ? "—"
          : valor !== null
            ? `${valor.toFixed(1)} kWh`
            : "Sin dato"}
      </div>
    </div>
  );
}
