import { useEffect, useState } from "react";
import { fetchAnomalia, fetchComparacion, fetchDetalleDia, fetchSerieDiaria } from "../api/consumo";
import type { AnomaliaResponse, ComparacionResponse, DetalleDiaResponse, DiarioResponse, PuntoSerie } from "../api/types";
import { CartelLatencia } from "../components/CartelLatencia";
import { GraficoConsumoDiario } from "../components/GraficoConsumoDiario";
import { PanelComparacion } from "../components/PanelComparacion";
import { PanelDetalleDia } from "../components/PanelDetalleDia";

interface SerieStats {
  maxPunto: PuntoSerie | null;
  minPunto: PuntoSerie | null;
  promedio: number | null;
  tendencia7d: "subiendo" | "bajando" | "estable" | null;
}

function calcularStats(serie: PuntoSerie[]): SerieStats {
  const conDato = serie.filter((p) => p.kwh > 0);
  if (conDato.length === 0) return { maxPunto: null, minPunto: null, promedio: null, tendencia7d: null };

  const maxPunto = conDato.reduce((a, b) => (b.kwh > a.kwh ? b : a));
  const minPunto = conDato.reduce((a, b) => (b.kwh < a.kwh ? b : a));
  const promedio = conDato.reduce((s, p) => s + p.kwh, 0) / conDato.length;

  let tendencia7d: SerieStats["tendencia7d"] = null;
  if (conDato.length >= 8) {
    const ultimos7 = conDato.slice(-7);
    const anteriores7 = conDato.slice(-14, -7);
    if (anteriores7.length >= 4) {
      const avgUlt = ultimos7.reduce((s, p) => s + p.kwh, 0) / ultimos7.length;
      const avgAnt = anteriores7.reduce((s, p) => s + p.kwh, 0) / anteriores7.length;
      const diff = (avgUlt - avgAnt) / avgAnt;
      if (diff > 0.05) tendencia7d = "subiendo";
      else if (diff < -0.05) tendencia7d = "bajando";
      else tendencia7d = "estable";
    }
  }

  return { maxPunto, minPunto, promedio, tendencia7d };
}

function formatFechaDia(fecha: string): string {
  const d = new Date(fecha + "T00:00:00");
  const dias = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
  return `${dias[d.getDay()]} ${d.getDate()}`;
}

interface StatsBarConsumoProps {
  stats: SerieStats;
  onClickMax?: () => void;
  onClickMin?: () => void;
}

function StatsBarConsumo({ stats, onClickMax, onClickMin }: StatsBarConsumoProps) {
  if (!stats.maxPunto && !stats.minPunto && stats.promedio === null) return null;

  const TENDENCIA_LABEL = { subiendo: "↑ Subiendo", bajando: "↓ Bajando", estable: "→ Estable" };
  const TENDENCIA_COLOR = { subiendo: "#b22c2c", bajando: "#1a7a4a", estable: "#6B5A45" };

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
        gap: 8,
        marginBottom: 16,
      }}
    >
      {stats.maxPunto && (
        <StatCard
          label="Día más alto"
          value={`${stats.maxPunto.kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`}
          sub={formatFechaDia(stats.maxPunto.fecha)}
          accentColor="#b22c2c"
          onClick={onClickMax}
          clickable={!!onClickMax}
        />
      )}
      {stats.minPunto && (
        <StatCard
          label="Día más bajo"
          value={`${stats.minPunto.kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`}
          sub={formatFechaDia(stats.minPunto.fecha)}
          accentColor="#1a7a4a"
          onClick={onClickMin}
          clickable={!!onClickMin}
        />
      )}
      {stats.promedio !== null && (
        <StatCard
          label="Promedio diario"
          value={`${stats.promedio.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`}
          sub="este mes"
          accentColor="#333"
        />
      )}
      {stats.tendencia7d && (
        <StatCard
          label="Últimos 7 días"
          value={TENDENCIA_LABEL[stats.tendencia7d]}
          sub="vs semana anterior"
          accentColor={TENDENCIA_COLOR[stats.tendencia7d]}
        />
      )}
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string;
  sub: string;
  accentColor: string;
  onClick?: () => void;
  clickable?: boolean;
}

function StatCard({ label, value, sub, accentColor, onClick, clickable }: StatCardProps) {
  return (
    <div
      onClick={onClick}
      style={{
        background: "#fff",
        border: "1px solid #E8DFD0",
        borderRadius: 8,
        padding: "10px 14px",
        cursor: clickable ? "pointer" : "default",
      }}
    >
      <p style={{ margin: 0, fontSize: 11, color: "#6B5A45", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
        {label}
      </p>
      <p style={{ margin: "4px 0 2px", fontSize: 15, fontWeight: 700, color: accentColor }}>
        {value}
      </p>
      <p style={{ margin: 0, fontSize: 11, color: "#999" }}>
        {sub}
      </p>
    </div>
  );
}

interface Props {
  token: string;
  suministroId: string;
}

function mesActualStr(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

function primerDiaMes(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
}

function hoy(): string {
  return new Date().toISOString().slice(0, 10);
}

export function ConsumoPage({ token, suministroId }: Props) {
  const [diario, setDiario] = useState<DiarioResponse | null>(null);
  const [comparacion, setComparacion] = useState<ComparacionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [anomalia, setAnomalia] = useState<AnomaliaResponse | null>(null);
  const [descargandoCsv, setDescargandoCsv] = useState(false);
  const [fechaSeleccionada, setFechaSeleccionada] = useState<string | null>(null);
  const [detalleDia, setDetalleDia] = useState<DetalleDiaResponse | null>(null);
  const [loadingDetalle, setLoadingDetalle] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);

    Promise.all([
      fetchSerieDiaria(token, suministroId, primerDiaMes(), hoy()),
      fetchComparacion(token, suministroId, mesActualStr()),
      fetchAnomalia(token, mesActualStr()).catch(() => null),
    ])
      .then(([d, c, a]) => {
        setDiario(d);
        setComparacion(c);
        setAnomalia(a);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Error al cargar datos");
      })
      .finally(() => setLoading(false));
  }, [token, suministroId]);

  function handleClickBarra(fecha: string) {
    setFechaSeleccionada(fecha);
    setDetalleDia(null);
    setLoadingDetalle(true);
    fetchDetalleDia(token, fecha)
      .then(setDetalleDia)
      .catch(() => setDetalleDia(null))
      .finally(() => setLoadingDetalle(false));
  }

  function handleExportarCsv() {
    setDescargandoCsv(true);
    const desde = primerDiaMes();
    const hasta = hoy();
    const url = `/consumo/export/csv?desde=${desde}&hasta=${hasta}`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const href = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = href;
        a.download = `consumo_${suministroId}_${desde}_${hasta}.csv`;
        a.click();
        URL.revokeObjectURL(href);
      })
      .finally(() => setDescargandoCsv(false));
  }

  function handleCerrarDetalle() {
    setFechaSeleccionada(null);
    setDetalleDia(null);
  }

  if (loading) {
    return <div style={{ padding: 24 }}>Cargando consumo...</div>;
  }

  if (error) {
    return <div style={{ padding: 24, color: "#c62828" }}>Error: {error}</div>;
  }

  const datosHasta = diario?.datos_hasta ?? comparacion?.datos_hasta ?? null;
  const stats = calcularStats(diario?.serie ?? []);

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "24px 16px", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <h2 style={{ margin: 0, fontSize: 22, color: "#1b5e20" }}>Mi Consumo</h2>
        {/* Botón visible solo en viewport ≥ 768px (función de alta densidad web, CU-C07) */}
        <button
          onClick={handleExportarCsv}
          disabled={descargandoCsv}
          data-testid="btn-exportar-csv"
          style={{
            display: "none",
            padding: "8px 16px",
            background: "#124e2f",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            fontSize: 13,
            fontWeight: 500,
            cursor: descargandoCsv ? "wait" : "pointer",
          }}
          className="export-csv-btn"
        >
          {descargandoCsv ? "Descargando..." : "Exportar CSV"}
        </button>
      </div>

      <CartelLatencia datosHasta={datosHasta} />

      {anomalia && (
        <div
          role="alert"
          data-testid="banner-anomalia"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "10px 16px",
            marginBottom: 16,
            background: "rgba(230,145,10,0.10)",
            border: "1px solid rgba(230,145,10,0.35)",
            borderRadius: 8,
            fontSize: 14,
            color: "#7a4a00",
          }}
        >
          <span style={{ fontSize: 18 }}>⚡</span>
          <span>
            El {new Date(anomalia.fecha + "T00:00:00").toLocaleDateString("es-AR", { weekday: "long", day: "numeric" })} tu consumo fue{" "}
            <strong>{Math.round(anomalia.desviacion_pct)}% mayor</strong> a tu promedio diario
            ({anomalia.kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh).
          </span>
        </div>
      )}

      <section style={{ marginBottom: 32 }}>
        <h3 style={{ fontSize: 16, color: "#333", marginBottom: 12 }}>Consumo diario (mes actual)</h3>
        <StatsBarConsumo
          stats={stats}
          onClickMax={stats.maxPunto ? () => handleClickBarra(stats.maxPunto!.fecha) : undefined}
          onClickMin={stats.minPunto ? () => handleClickBarra(stats.minPunto!.fecha) : undefined}
        />
        <GraficoConsumoDiario
          serie={diario?.serie ?? []}
          onClickBarra={handleClickBarra}
          maxFecha={stats.maxPunto?.fecha}
          minFecha={stats.minPunto?.fecha}
        />
      </section>

      {fechaSeleccionada && (
        <PanelDetalleDia
          fecha={fechaSeleccionada}
          detalle={detalleDia}
          loading={loadingDetalle}
          onCerrar={handleCerrarDetalle}
        />
      )}

      <section>
        <h3 style={{ fontSize: 16, color: "#333", marginBottom: 12 }}>Comparación histórica</h3>
        {comparacion ? (
          <PanelComparacion
            mesActual={comparacion.mes_actual}
            mesAnterior={comparacion.mes_anterior}
            mismoMesAnioAnterior={comparacion.mismo_mes_anio_anterior}
          />
        ) : null}
      </section>
    </div>
  );
}
