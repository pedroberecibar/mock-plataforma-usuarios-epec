import { useEffect, useRef, useState } from "react";
import type { HomeResponse } from "../api/types";
import { fetchHome } from "../api/home";
import { fetchPerfil, type PerfilResponse } from "../api/usuario";
import { BloqueConsumoMes } from "../components/BloqueConsumoMes";
import { BloqueZona } from "../components/BloqueZona";
import { BloqueProyeccion } from "../components/BloqueProyeccion";
import { BloqueAccesos } from "../components/BloqueAccesos";
import { HeroSaludo } from "../components/HeroSaludo";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { AlertBanner } from "../components/AlertBanner";
import { ToastCargando } from "../components/ToastCargando";
import type { Vista } from "../components/AppShell";
import {
  bg,
  fg,
  font,
  fontSize,
  space,
  border,
} from "../design-tokens";

function mesActualYYYYMM(): string {
  const now = new Date();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  return `${now.getFullYear()}-${m}`;
}

interface Props {
  token: string;
  suministroId: string;
  nombre?: string | null;
  nroSuministro?: string;
  mes?: string;
  onNavegar?: (vista: Vista) => void;
}

const _POLL_INTERVAL_MS = 12_000;
const _POLL_MAX_MS = 180_000;

export function HomePage({ token, suministroId, nombre, nroSuministro, mes, onNavegar }: Props) {
  const [data, setData] = useState<HomeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [perfil, setPerfil] = useState<PerfilResponse | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const mesStr = mes ?? mesActualYYYYMM();
  const dataReady = data?.consumo_mes.total_kwh != null;

  // Limpia timers al desmontar
  useEffect(() => () => {
    if (pollRef.current) clearInterval(pollRef.current);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
  }, []);

  // Carga inicial de datos del home
  useEffect(() => {
    setLoading(true);
    fetchHome(token, mesStr)
      .then(setData)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Error desconocido")
      )
      .finally(() => setLoading(false));
  }, [token, suministroId, mesStr]);

  // Fetch perfil para tarifa (no bloquea el render)
  useEffect(() => {
    fetchPerfil(token)
      .then(setPerfil)
      .catch(() => {});
  }, [token]);

  // Polling mientras los datos no estén disponibles
  useEffect(() => {
    if (loading || dataReady || error) return;

    pollRef.current = setInterval(() => {
      fetchHome(token, mesStr)
        .then((d) => {
          setData(d);
          if (d.consumo_mes.total_kwh != null) {
            if (pollRef.current) clearInterval(pollRef.current);
            if (timeoutRef.current) clearTimeout(timeoutRef.current);
          }
        })
        .catch(() => {});
    }, _POLL_INTERVAL_MS);

    timeoutRef.current = setTimeout(() => {
      if (pollRef.current) clearInterval(pollRef.current);
    }, _POLL_MAX_MS);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [loading, dataReady, error, token, mesStr]);

  const heroNombre = nombre ?? perfil?.nombre ?? null;
  const heroNroSuministro = nroSuministro ?? perfil?.nro_suministro ?? suministroId;
  const heroTarifa = perfil?.tarifa_codigo ?? null;

  if (loading) {
    return (
      <div style={{ background: bg.page, minHeight: "100%" }}>
        <HeroSaludo nombre={heroNombre} nroSuministro={heroNroSuministro} tarifaCodigo={heroTarifa} />
        <div style={{ padding: `${space[10]}px`, maxWidth: 1400, margin: "0 auto" }}>
          <div style={{
            display:             "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap:                 space[6],
          }}>
            <LoadingSkeleton variant="card" />
            <LoadingSkeleton variant="card" />
            <LoadingSkeleton variant="card" />
            <LoadingSkeleton variant="card" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: bg.page, minHeight: "100%" }}>
        <HeroSaludo nombre={heroNombre} nroSuministro={heroNroSuministro} tarifaCodigo={heroTarifa} />
        <div style={{ padding: `${space[10]}px`, maxWidth: 1400, margin: "0 auto" }}>
          <AlertBanner variant="error">Error al cargar: {error}</AlertBanner>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const tsDate = new Date(data.timestamp).toLocaleString("es-AR", {
    timeZone:  "America/Argentina/Cordoba",
    day:       "numeric",
    month:     "short",
    hour:      "2-digit",
    minute:    "2-digit",
  });

  return (
    <div style={{ minHeight: "100%", background: bg.page, fontFamily: font.sans }}>
      <HeroSaludo nombre={heroNombre} nroSuministro={heroNroSuministro} tarifaCodigo={heroTarifa} />

      <main aria-label="home del cliente">
        <div style={{
          maxWidth: 1400,
          margin:   "0 auto",
          padding:  `${space[10]}px`,
        }}>
          {!dataReady && <ToastCargando />}

          <div style={{
            display:             "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap:                 space[6],
          }}>
            <BloqueConsumoMes consumoMes={data.consumo_mes} />
            <BloqueZona zona={data.comparacion_zona} />
            <BloqueProyeccion proyeccion={data.proyeccion} />
            <BloqueAccesos suministroId={suministroId} onNavegar={onNavegar} />
          </div>

          <footer style={{
            marginTop:      space[10],
            paddingTop:     space[6],
            borderTop:      `1px solid ${border.default}`,
            display:        "flex",
            justifyContent: "flex-end",
          }}>
            <p style={{
              fontFamily:    font.mono,
              fontSize:      fontSize.xs,
              letterSpacing: "0.05em",
              color:         fg.muted,
              margin:        0,
            }}>
              Actualizado: {tsDate}
            </p>
          </footer>
        </div>
      </main>
    </div>
  );
}
