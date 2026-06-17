import { useEffect, useState } from "react";
import { fetchComparacion, fetchSerieDiaria } from "../api/consumo";
import type { ComparacionResponse, DiarioResponse } from "../api/types";
import { CartelLatencia } from "../components/CartelLatencia";
import { GraficoConsumoDiario } from "../components/GraficoConsumoDiario";
import { PanelComparacion } from "../components/PanelComparacion";

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

  useEffect(() => {
    setLoading(true);
    setError(null);

    Promise.all([
      fetchSerieDiaria(token, suministroId, primerDiaMes(), hoy()),
      fetchComparacion(token, suministroId, mesActualStr()),
    ])
      .then(([d, c]) => {
        setDiario(d);
        setComparacion(c);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Error al cargar datos");
      })
      .finally(() => setLoading(false));
  }, [token, suministroId]);

  if (loading) {
    return <div style={{ padding: 24 }}>Cargando consumo...</div>;
  }

  if (error) {
    return <div style={{ padding: 24, color: "#c62828" }}>Error: {error}</div>;
  }

  const datosHasta = diario?.datos_hasta ?? comparacion?.datos_hasta ?? null;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "24px 16px", fontFamily: "sans-serif" }}>
      <h2 style={{ margin: "0 0 16px", fontSize: 22, color: "#1b5e20" }}>Mi Consumo</h2>

      <CartelLatencia datosHasta={datosHasta} />

      <section style={{ marginBottom: 32 }}>
        <h3 style={{ fontSize: 16, color: "#333", marginBottom: 12 }}>Consumo diario (mes actual)</h3>
        <GraficoConsumoDiario serie={diario?.serie ?? []} />
      </section>

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
