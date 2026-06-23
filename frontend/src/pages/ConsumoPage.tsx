import { useEffect, useState } from "react";
import { fetchAnomalia, fetchComparacion, fetchDetalleDia, fetchHoraPico, fetchSerieDiaria, fetchSerieHoraria } from "../api/consumo";
import { fetchObjetivoEstado } from "../api/objetivos";
import type { AnomaliaResponse, ComparacionResponse, DetalleDiaResponse, DiarioResponse, HoraPicoResponse, ObjetivoEstadoResponse, PuntoSerie, SerieHorariaResponse } from "../api/types";
import { CartelLatencia } from "../components/CartelLatencia";
import { GraficoConsumoDiario } from "../components/GraficoConsumoDiario";
import { PanelComparacion } from "../components/PanelComparacion";
import { PanelDetalleDia } from "../components/PanelDetalleDia";
import { PanelVecinosComparacion } from "../components/PanelVecinosComparacion";
import { PageHeader } from "../components/PageHeader";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { AlertBanner } from "../components/AlertBanner";
import { SectionTitle } from "../components/SectionTitle";
import { StatMiniCard } from "../components/StatMiniCard";
import {
  bg,
  brand,
  color,
  fg,
  font,
  fontSize,
  fontWeight,
  radius,
  space,
} from "../design-tokens";

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

const TENDENCIA_LABEL = { subiendo: "↑ Subiendo", bajando: "↓ Bajando", estable: "→ Estable" };
const TENDENCIA_COLOR = {
  subiendo: color.errorDark,
  bajando:  color.successDark,
  estable:  fg.secondary,
};

interface StatsBarConsumoProps {
  stats: SerieStats;
  horaPico?: HoraPicoResponse | null;
  onClickMax?: () => void;
  onClickMin?: () => void;
}

function StatsBarConsumo({ stats, horaPico, onClickMax, onClickMin }: StatsBarConsumoProps) {
  if (!stats.maxPunto && !stats.minPunto && stats.promedio === null && !horaPico) return null;

  return (
    <div
      style={{
        display:             "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
        gap:                 space[2],
        marginBottom:        space[4],
      }}
    >
      {stats.maxPunto && (
        <StatMiniCard
          label="Día más alto"
          value={`${stats.maxPunto.kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`}
          sub={formatFechaDia(stats.maxPunto.fecha)}
          accentColor={color.errorDark}
          onClick={onClickMax}
        />
      )}
      {stats.minPunto && (
        <StatMiniCard
          label="Día más bajo"
          value={`${stats.minPunto.kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`}
          sub={formatFechaDia(stats.minPunto.fecha)}
          accentColor={color.successDark}
          onClick={onClickMin}
        />
      )}
      {stats.promedio !== null && (
        <StatMiniCard
          label="Promedio diario"
          value={`${stats.promedio.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`}
          sub="este mes"
        />
      )}
      {stats.tendencia7d && (
        <StatMiniCard
          label="Últimos 7 días"
          value={TENDENCIA_LABEL[stats.tendencia7d]}
          sub="vs semana anterior"
          accentColor={TENDENCIA_COLOR[stats.tendencia7d]}
        />
      )}
      {horaPico && (
        <StatMiniCard
          label="Hora pico del mes"
          value={`${String(horaPico.hora_pico).padStart(2, "0")}:00 hs`}
          sub={`${horaPico.kwh_promedio.toFixed(1)} kWh promedio`}
          accentColor={color.successDark}
        />
      )}
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
  const [objetivoEstado, setObjetivoEstado] = useState<ObjetivoEstadoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [anomalia, setAnomalia] = useState<AnomaliaResponse | null>(null);
  const [descargandoCsv, setDescargandoCsv] = useState(false);
  const [fechaSeleccionada, setFechaSeleccionada] = useState<string | null>(null);
  const [detalleDia, setDetalleDia] = useState<DetalleDiaResponse | null>(null);
  const [loadingDetalle, setLoadingDetalle] = useState(false);
  const [detalleHorario, setDetalleHorario] = useState<SerieHorariaResponse | null>(null);
  const [horaPico, setHoraPico] = useState<HoraPicoResponse | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    Promise.all([
      fetchSerieDiaria(token, suministroId, primerDiaMes(), hoy()),
      fetchComparacion(token, suministroId, mesActualStr()),
      fetchAnomalia(token, mesActualStr()).catch(() => null),
      fetchObjetivoEstado(token, mesActualStr()).catch(() => null),
      fetchHoraPico(token, mesActualStr()).catch(() => null),
    ])
      .then(([d, c, a, oe, hp]) => {
        setDiario(d);
        setComparacion(c);
        setAnomalia(a);
        setObjetivoEstado(oe);
        setHoraPico(hp);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Error al cargar datos");
      })
      .finally(() => setLoading(false));
  }, [token, suministroId]);

  function handleClickBarra(fecha: string) {
    setFechaSeleccionada(fecha);
    setDetalleDia(null);
    setDetalleHorario(null);
    setLoadingDetalle(true);
    fetchDetalleDia(token, fecha)
      .then(setDetalleDia)
      .catch(() => setDetalleDia(null))
      .finally(() => setLoadingDetalle(false));
    fetchSerieHoraria(token, fecha)
      .then(setDetalleHorario)
      .catch(() => setDetalleHorario(null));
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
    setDetalleHorario(null);
  }

  const exportButton = (
    <button
      onClick={handleExportarCsv}
      disabled={descargandoCsv}
      data-testid="btn-exportar-csv"
      className="export-csv-btn"
      style={{
        padding:      `${space[2]}px ${space[4]}px`,
        background:   brand.primary,
        color:        fg.onDark,
        border:       "none",
        borderRadius: radius.sm,
        fontSize:     fontSize.sm,
        fontWeight:   fontWeight.medium,
        fontFamily:   font.sans,
        cursor:       descargandoCsv ? "wait" : "pointer",
      }}
    >
      {descargandoCsv ? "Descargando..." : "Exportar CSV"}
    </button>
  );

  if (loading) {
    return (
      <div style={{ background: bg.page, minHeight: "100%" }}>
        <PageHeader title="Mi Consumo" actions={exportButton} />
        <div style={{ padding: `${space[10]}px`, maxWidth: 1400, margin: "0 auto" }}>
          <LoadingSkeleton variant="card" />
          <div style={{ height: space[6] }} />
          <LoadingSkeleton variant="chart" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: bg.page, minHeight: "100%" }}>
        <PageHeader title="Mi Consumo" actions={exportButton} />
        <div style={{ padding: `${space[10]}px`, maxWidth: 1400, margin: "0 auto" }}>
          <AlertBanner variant="error">Error: {error}</AlertBanner>
        </div>
      </div>
    );
  }

  const datosHasta = diario?.datos_hasta ?? comparacion?.datos_hasta ?? null;
  const stats = calcularStats(diario?.serie ?? []);

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <PageHeader title="Mi Consumo" actions={exportButton} />

      <main aria-label="consumo del cliente">
        <div style={{ maxWidth: 1400, margin: "0 auto", padding: `${space[10]}px` }}>

          <CartelLatencia datosHasta={datosHasta} />

          {anomalia && (
            <div style={{ marginBottom: space[4] }}>
              <AlertBanner variant="warning">
                ⚡ El {new Date(anomalia.fecha + "T00:00:00").toLocaleDateString("es-AR", { weekday: "long", day: "numeric" })} tu consumo fue{" "}
                <strong>{Math.round(anomalia.desviacion_pct)}% mayor</strong> a tu promedio diario
                ({anomalia.kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh).
              </AlertBanner>
            </div>
          )}

          <section style={{ marginBottom: space[8] }}>
            <SectionTitle marginBottom={space[4]}>Consumo diario (mes actual)</SectionTitle>
            <StatsBarConsumo
              stats={stats}
              horaPico={horaPico}
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
              serieHoraria={detalleHorario?.serie}
            />
          )}

          <section style={{ marginBottom: space[8] }}>
            <SectionTitle marginBottom={space[4]}>Comparación histórica</SectionTitle>
            {comparacion ? (
              <PanelComparacion
                mesActual={comparacion.mes_actual}
                mesAnterior={comparacion.mes_anterior}
                mismoMesAnioAnterior={comparacion.mismo_mes_anio_anterior}
              />
            ) : null}
          </section>

          {comparacion && (
            <section style={{ marginBottom: space[8] }}>
              <PanelVecinosComparacion
                zona={comparacion.zona_mes_actual}
                mesActual={comparacion.mes_actual}
                mismoMesAnioAnterior={comparacion.mismo_mes_anio_anterior}
                objetivoDiarioKwh={objetivoEstado?.consumo_diario_objetivo_kwh ?? null}
              />
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
