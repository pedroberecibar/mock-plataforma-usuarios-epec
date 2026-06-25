import { useEffect, useState } from "react";
import { fetchAnomalia, fetchComparacion, fetchDetalleDia, fetchSerieDiaria, fetchSerieHoraria } from "../api/consumo";
import { fetchObjetivo, fetchObjetivoEstado, type ObjetivoResponse } from "../api/objetivos";
import type { AnomaliaResponse, ComparacionResponse, DetalleDiaResponse, DiarioResponse, ObjetivoEstadoResponse, PuntoSerie, SerieHorariaResponse } from "../api/types";
import { CartelLatencia } from "../components/CartelLatencia";
import { GraficoConsumoDiario } from "../components/GraficoConsumoDiario";
import { ObjetivoResumenCard } from "../components/ObjetivoResumenCard";
import { PanelDetalleDia } from "../components/PanelDetalleDia";
import { PanelVecinosComparacion } from "../components/PanelVecinosComparacion";
import { PageHeader } from "../components/PageHeader";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { AlertBanner } from "../components/AlertBanner";
import {
  bg,
  brand,
  color,
  fg,
  font,
  fontSize,
  fontWeight,
  radius,
  shadow,
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

function formatMes(fecha: string): string {
  const [year, month] = fecha.split("-");
  const d = new Date(parseInt(year), parseInt(month) - 1, 1);
  return d.toLocaleDateString("es-AR", { month: "long", year: "numeric" });
}

// Card fila superior: número kWh hero (igual estilo que home)
function KpiCard({ label, sublabel, kwh }: { label: string; sublabel: string; kwh: number | null }) {
  return (
    <div style={{
      background:   bg.surfaceFeat,
      borderRadius: `${radius.lg}px`,
      boxShadow:    shadow.sm,
      padding:      `${space[5]}px`,
      fontFamily:   font.sans,
    }}>
      <p style={{
        margin:        0,
        fontSize:      fontSize.xs,
        fontWeight:    fontWeight.semibold,
        color:         fg.secondary,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
      }}>
        {label}
      </p>
      <p style={{ margin: `${space[1]}px 0`, fontSize: fontSize.xs, color: fg.muted }}>
        {sublabel}
      </p>
      {kwh !== null ? (
        <p style={{
          margin:        0,
          fontFamily:    font.technical,
          fontSize:      fontSize["2xl"],
          fontWeight:    fontWeight.light,
          color:         fg.link,
          lineHeight:    1.2,
          letterSpacing: "-0.02em",
        }}>
          {kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })}
          <span style={{
            fontFamily:  font.sans,
            fontSize:    fontSize.sm,
            fontWeight:  fontWeight.regular,
            color:       fg.secondary,
            marginLeft:  space[1],
          }}>kWh</span>
        </p>
      ) : (
        <p style={{ margin: 0, fontSize: fontSize.md, color: fg.muted }}>—</p>
      )}
    </div>
  );
}

// Card fila inferior: stat con valor destacado (igual estilo que home, sin borde)
function StatFeatCard({
  label, value, sub, accentColor, onClick,
}: {
  label: string; value: string; sub: string; accentColor?: string; onClick?: () => void;
}) {
  const clickable = !!onClick;
  return (
    <div
      onClick={onClick}
      style={{
        background:   bg.surfaceFeat,
        borderRadius: `${radius.lg}px`,
        boxShadow:    shadow.sm,
        padding:      `${space[4]}px ${space[5]}px`,
        fontFamily:   font.sans,
        cursor:       clickable ? "pointer" : "default",
        transition:   clickable ? "box-shadow 150ms ease, transform 150ms ease" : undefined,
      }}
      onMouseEnter={clickable ? (e) => {
        (e.currentTarget as HTMLElement).style.boxShadow = shadow.md;
        (e.currentTarget as HTMLElement).style.transform = "translateY(-1px)";
      } : undefined}
      onMouseLeave={clickable ? (e) => {
        (e.currentTarget as HTMLElement).style.boxShadow = shadow.sm;
        (e.currentTarget as HTMLElement).style.transform = "";
      } : undefined}
    >
      <p style={{
        margin:        0,
        fontSize:      fontSize.xs,
        fontWeight:    fontWeight.semibold,
        color:         fg.secondary,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
      }}>
        {label}
      </p>
      <p style={{
        margin:     `${space[1]}px 0`,
        fontFamily: font.technical,
        fontSize:   fontSize.md,
        fontWeight: fontWeight.bold,
        color:      accentColor ?? fg.primary,
        lineHeight: 1.2,
      }}>
        {value}
      </p>
      <p style={{ margin: 0, fontSize: fontSize.xs, color: fg.muted }}>
        {sub}
      </p>
    </div>
  );
}

interface Props {
  token: string;
  suministroId: string;
  onEditarObjetivo?: () => void;
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

export function ConsumoPage({ token, suministroId, onEditarObjetivo }: Props) {
  const [diario, setDiario] = useState<DiarioResponse | null>(null);
  const [comparacion, setComparacion] = useState<ComparacionResponse | null>(null);
  const [objetivo, setObjetivo] = useState<ObjetivoResponse | null>(null);
  const [objetivoEstado, setObjetivoEstado] = useState<ObjetivoEstadoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [anomalia, setAnomalia] = useState<AnomaliaResponse | null>(null);
  const [descargandoCsv, setDescargandoCsv] = useState(false);
  const [fechaSeleccionada, setFechaSeleccionada] = useState<string | null>(null);
  const [detalleDia, setDetalleDia] = useState<DetalleDiaResponse | null>(null);
  const [loadingDetalle, setLoadingDetalle] = useState(false);
  const [detalleHorario, setDetalleHorario] = useState<SerieHorariaResponse | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    Promise.all([
      fetchSerieDiaria(token, suministroId, primerDiaMes(), hoy()),
      fetchComparacion(token, suministroId, mesActualStr()),
      fetchAnomalia(token, mesActualStr()).catch(() => null),
      fetchObjetivoEstado(token, mesActualStr()).catch(() => null),
      fetchObjetivo(token).catch(() => null),
    ])
      .then(([d, c, a, oe, obj]) => {
        setDiario(d);
        setComparacion(c);
        setAnomalia(a);
        setObjetivoEstado(oe);
        setObjetivo(obj);
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

          <ObjetivoResumenCard
            objetivo={objetivo}
            estado={objetivoEstado}
            onEditar={() => onEditarObjetivo?.()}
          />

          {anomalia && (
            <div style={{ marginBottom: space[4] }}>
              <AlertBanner variant="warning">
                ⚡ El {new Date(anomalia.fecha + "T00:00:00").toLocaleDateString("es-AR", { weekday: "long", day: "numeric" })} tu consumo fue{" "}
                <strong>{Math.round(anomalia.desviacion_pct)}% mayor</strong> a tu promedio diario
                ({anomalia.kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh).
              </AlertBanner>
            </div>
          )}

          {/* Resumen del mes: dos filas de 4 cards */}
          <section style={{ marginBottom: space[8] }}>
            {/* Fila superior: totales históricos */}
            <div style={{
              display:             "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap:                 space[3],
              marginBottom:        space[3],
            }}>
              <KpiCard
                label="Consumo mes actual"
                sublabel={comparacion ? formatMes(comparacion.mes_actual.mes) : ""}
                kwh={comparacion?.mes_actual.total_kwh ?? null}
              />
              <KpiCard
                label="Mes anterior"
                sublabel={comparacion ? formatMes(comparacion.mes_anterior.mes) : ""}
                kwh={comparacion?.mes_anterior.total_kwh ?? null}
              />
              <KpiCard
                label="Mismo mes año anterior"
                sublabel={comparacion ? formatMes(comparacion.mismo_mes_anio_anterior.mes) : ""}
                kwh={comparacion?.mismo_mes_anio_anterior.total_kwh ?? null}
              />
              <KpiCard
                label="Promedio diario"
                sublabel="este mes"
                kwh={stats.promedio ?? null}
              />
            </div>

            {/* Fila inferior: stats del mes actual */}
            <div style={{
              display:             "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap:                 space[3],
              marginBottom:        space[6],
            }}>
              <StatFeatCard
                label="Día más alto"
                value={stats.maxPunto
                  ? `${stats.maxPunto.kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`
                  : "—"}
                sub={stats.maxPunto ? formatFechaDia(stats.maxPunto.fecha) : ""}
                accentColor={color.errorDark}
                onClick={stats.maxPunto ? () => handleClickBarra(stats.maxPunto!.fecha) : undefined}
              />
              <StatFeatCard
                label="Día más bajo"
                value={stats.minPunto
                  ? `${stats.minPunto.kwh.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`
                  : "—"}
                sub={stats.minPunto ? formatFechaDia(stats.minPunto.fecha) : ""}
                accentColor={color.successDark}
                onClick={stats.minPunto ? () => handleClickBarra(stats.minPunto!.fecha) : undefined}
              />
              <StatFeatCard
                label="Promedio diario"
                value={stats.promedio !== null
                  ? `${stats.promedio.toLocaleString("es-AR", { maximumFractionDigits: 1 })} kWh`
                  : "—"}
                sub="este mes"
              />
              <StatFeatCard
                label="Últimos 7 días"
                value={stats.tendencia7d ? TENDENCIA_LABEL[stats.tendencia7d] : "—"}
                sub="vs semana anterior"
                accentColor={stats.tendencia7d ? TENDENCIA_COLOR[stats.tendencia7d] : fg.muted}
              />
            </div>
          </section>

          <section style={{ marginBottom: space[8] }}>
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
