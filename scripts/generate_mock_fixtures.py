#!/usr/bin/env python3
"""Generate static JSON fixtures for the GitHub Pages demo build.

Reads directly from SQLite — no FastAPI, no project imports.
Run once from the project root before committing the demo fixtures:

    python scripts/generate_mock_fixtures.py

Output goes to frontend/public/mock-data/ (committed to git).
The DB stays local; only the computed JSON snapshots are versioned.
"""

from __future__ import annotations

import calendar
import json
import math
import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

DB_PATH = Path("data/plataforma_clientes.db")
OUT_DIR = Path("frontend/public/mock-data")
SUMINISTRO_ID = "SRV-91013496"
MES = date(2026, 6, 1)
RADIO_METROS = 150.0
MIN_VECINOS = 5
DIAS_SEMANA = 364  # 52 semanas → mismo día-de-semana año anterior


# ---------------------------------------------------------------------------
# Helpers de consulta
# ---------------------------------------------------------------------------


def get_serie(
    conn: sqlite3.Connection, sid: str, desde: date, hasta: date
) -> list[tuple[date, float]]:
    rows = conn.execute(
        "SELECT fecha, kwh FROM consumo_diario"
        " WHERE suministro_id=? AND fecha>=? AND fecha<=? ORDER BY fecha",
        (sid, desde.isoformat(), hasta.isoformat()),
    ).fetchall()
    return [(date.fromisoformat(r[0]), float(r[1])) for r in rows]


def get_ultima_fecha(conn: sqlite3.Connection, sid: str) -> date | None:
    row = conn.execute(
        "SELECT MAX(fecha) FROM consumo_diario WHERE suministro_id=?", (sid,)
    ).fetchone()
    return date.fromisoformat(row[0]) if row and row[0] else None


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return r * 2 * math.asin(math.sqrt(a))


def get_vecinos(conn: sqlite3.Connection, sid: str) -> list[str]:
    ref = conn.execute(
        "SELECT lat, lon, tarifa_codigo FROM suministros WHERE id=?", (sid,)
    ).fetchone()
    if not ref:
        return []
    lat_ref, lon_ref, tarifa_ref = ref
    delta = RADIO_METROS / 111_000.0

    query = (
        "SELECT id, lat, lon FROM suministros"
        " WHERE id != ?"
        "   AND lat BETWEEN ? AND ?"
        "   AND lon BETWEEN ? AND ?"
    )
    params: list[object] = [sid, lat_ref - delta, lat_ref + delta, lon_ref - delta, lon_ref + delta]
    if tarifa_ref is not None:
        query += " AND tarifa_codigo = ?"
        params.append(tarifa_ref)

    rows = conn.execute(query, params).fetchall()
    return [r[0] for r in rows if haversine(lat_ref, lon_ref, r[1], r[2]) <= RADIO_METROS]


# ---------------------------------------------------------------------------
# Proyección mensual (método interanual → estacional → reciente)
# ---------------------------------------------------------------------------


def _calcular_proyeccion(conn: sqlite3.Connection, sid: str, mes: date) -> dict:
    days_in_month = calendar.monthrange(mes.year, mes.month)[1]
    mes_fin = mes.replace(day=days_in_month)
    current_serie = get_serie(conn, sid, mes, mes_fin)
    dias_actuales = len(current_serie)

    if dias_actuales > 0:
        ly_inicio = mes.replace(year=mes.year - 1)
        ly_fin = ly_inicio.replace(day=calendar.monthrange(ly_inicio.year, ly_inicio.month)[1])
        ly_serie = get_serie(conn, sid, ly_inicio, ly_fin)
        if len(ly_serie) >= 20:
            ly_dict = {d.day: kwh for d, kwh in ly_serie}
            current_days = sorted(d.day for d, _ in current_serie)
            total_current = sum(kwh for _, kwh in current_serie)
            total_same_ly = sum(ly_dict.get(dia, 0.0) for dia in current_days)
            total_ly = sum(kwh for _, kwh in ly_serie)
            ratio = total_current / total_same_ly if total_same_ly > 0 else 1.0
            projected = ratio * total_ly
            return {
                "mes": mes.isoformat(),
                "metodo_aplicado": "interanual",
                "bandera_confianza": "alta",
                "rango_inferior_kwh": round(projected * 0.9, 2),
                "rango_superior_kwh": round(projected * 1.1, 2),
            }

    return {
        "mes": mes.isoformat(),
        "metodo_aplicado": "insuficiente",
        "bandera_confianza": "sin_datos",
        "rango_inferior_kwh": None,
        "rango_superior_kwh": None,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def build_home(conn: sqlite3.Connection, sid: str, mes: date) -> dict:
    days_in_month = calendar.monthrange(mes.year, mes.month)[1]
    mes_fin = mes.replace(day=days_in_month)
    current_serie = get_serie(conn, sid, mes, mes_fin)
    total_kwh = round(sum(kwh for _, kwh in current_serie), 2) if current_serie else None
    dias_transcurridos = len(current_serie)

    vs_mes_anterior_pct = None
    if total_kwh is not None and dias_transcurridos > 0:
        prev_inicio = (
            date(mes.year, mes.month - 1, 1) if mes.month > 1 else date(mes.year - 1, 12, 1)
        )
        days_in_prev = calendar.monthrange(prev_inicio.year, prev_inicio.month)[1]
        prev_fin = prev_inicio.replace(day=min(dias_transcurridos, days_in_prev))
        prev_serie = get_serie(conn, sid, prev_inicio, prev_fin)
        prev_total = sum(kwh for _, kwh in prev_serie) if prev_serie else 0.0
        if prev_total > 0:
            vs_mes_anterior_pct = round((total_kwh - prev_total) / prev_total * 100, 2)

    vs_anio_anterior_pct = None
    if total_kwh is not None and dias_transcurridos > 0:
        ly_inicio = mes.replace(year=mes.year - 1)
        days_in_ly = calendar.monthrange(ly_inicio.year, ly_inicio.month)[1]
        ly_fin = ly_inicio.replace(day=min(dias_transcurridos, days_in_ly))
        ly_serie = get_serie(conn, sid, ly_inicio, ly_fin)
        ly_total = sum(kwh for _, kwh in ly_serie) if ly_serie else 0.0
        if ly_total > 0:
            vs_anio_anterior_pct = round((total_kwh - ly_total) / ly_total * 100, 2)

    vecinos = get_vecinos(conn, sid)
    n_vecinos = len(vecinos)
    promedio_vecinos_kwh = None
    diferencia_pct = None
    if n_vecinos >= MIN_VECINOS and dias_transcurridos > 0:
        vecino_totals = [
            sum(kwh for _, kwh in vs)
            for vid in vecinos
            if (vs := get_serie(conn, vid, mes, mes_fin))
        ]
        if len(vecino_totals) >= MIN_VECINOS:
            promedio = sum(vecino_totals) / len(vecino_totals)
            promedio_vecinos_kwh = round(promedio, 2)
            if promedio > 0 and total_kwh is not None:
                diferencia_pct = round((total_kwh - promedio) / promedio * 100, 2)

    datos_hasta = get_ultima_fecha(conn, sid)
    proyeccion = _calcular_proyeccion(conn, sid, mes)

    return {
        "consumo_mes": {
            "total_kwh": total_kwh,
            "vs_mes_anterior_pct": vs_mes_anterior_pct,
            "vs_anio_anterior_pct": vs_anio_anterior_pct,
        },
        "comparacion_zona": {
            "promedio_vecinos_kwh": promedio_vecinos_kwh,
            "n_vecinos": n_vecinos,
            "diferencia_pct": diferencia_pct,
        },
        "proyeccion": proyeccion,
        "datos_hasta": datos_hasta.isoformat() if datos_hasta else None,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def build_diario(conn: sqlite3.Connection, sid: str) -> dict:
    desde = date(MES.year, 1, 1)
    hasta = get_ultima_fecha(conn, sid)
    if not hasta:
        return {"serie": [], "datos_hasta": None}
    serie = get_serie(conn, sid, desde, hasta)
    return {
        "serie": [{"fecha": d.isoformat(), "kwh": kwh} for d, kwh in serie],
        "datos_hasta": hasta.isoformat(),
    }


def build_comparacion(conn: sqlite3.Connection, sid: str, mes: date) -> dict:
    def get_periodo(primer: date) -> dict:
        _, last_day = calendar.monthrange(primer.year, primer.month)
        serie = get_serie(conn, sid, primer, primer.replace(day=last_day))
        total = round(sum(kwh for _, kwh in serie), 2) if serie else None
        return {
            "mes": primer.isoformat(),
            "serie": [{"fecha": d.isoformat(), "kwh": kwh} for d, kwh in serie],
            "total_kwh": total,
        }

    anterior = date(mes.year, mes.month - 1, 1) if mes.month > 1 else date(mes.year - 1, 12, 1)
    datos_hasta = get_ultima_fecha(conn, sid)
    return {
        "mes_actual": get_periodo(mes),
        "mes_anterior": get_periodo(anterior),
        "mismo_mes_anio_anterior": get_periodo(mes.replace(year=mes.year - 1)),
        "datos_hasta": datos_hasta.isoformat() if datos_hasta else None,
    }


def build_detalle_dia(conn: sqlite3.Connection, sid: str) -> dict:
    vecinos = get_vecinos(conn, sid)
    ultima = get_ultima_fecha(conn, sid)
    if not ultima:
        return {}

    result: dict[str, dict] = {}
    for i in range(60):
        fecha = ultima - timedelta(days=i)
        fecha_str = fecha.isoformat()

        row = conn.execute(
            "SELECT kwh FROM consumo_diario WHERE suministro_id=? AND fecha=?",
            (sid, fecha_str),
        ).fetchone()
        kwh_dia = float(row[0]) if row else None

        fecha_ant = fecha - timedelta(days=DIAS_SEMANA)
        row_ant = conn.execute(
            "SELECT kwh FROM consumo_diario WHERE suministro_id=? AND fecha=?",
            (sid, fecha_ant.isoformat()),
        ).fetchone()
        kwh_mismo_dia_anio_ant = float(row_ant[0]) if row_ant else None

        totales_v = []
        for vid in vecinos:
            rv = conn.execute(
                "SELECT kwh FROM consumo_diario WHERE suministro_id=? AND fecha=?",
                (vid, fecha_str),
            ).fetchone()
            if rv:
                totales_v.append(float(rv[0]))

        n_v = len(totales_v)
        kwh_promedio_zona = round(sum(totales_v) / n_v, 2) if n_v >= MIN_VECINOS else None

        result[fecha_str] = {
            "fecha": fecha_str,
            "kwh_dia": kwh_dia,
            "kwh_mismo_dia_anio_ant": kwh_mismo_dia_anio_ant,
            "kwh_promedio_zona": kwh_promedio_zona,
            "n_vecinos": n_v,
        }

    return result


def build_anomalia(conn: sqlite3.Connection, sid: str, mes: date) -> dict | None:
    _, last_day = calendar.monthrange(mes.year, mes.month)
    serie = get_serie(conn, sid, mes, mes.replace(day=last_day))
    if len(serie) < 3:
        return None

    valores = [kwh for _, kwh in serie]
    n = len(valores)
    media = sum(valores) / n
    varianza = sum((v - media) ** 2 for v in valores) / n
    std = math.sqrt(varianza)
    if std == 0:
        return None

    ultima_fecha, ultimo_kwh = serie[-1]
    z = (ultimo_kwh - media) / std
    if z <= 2.0:
        return None

    desviacion_pct = ((ultimo_kwh - media) / media) * 100 if media != 0 else 0.0
    return {
        "fecha": ultima_fecha.isoformat(),
        "kwh": ultimo_kwh,
        "z_score": round(z, 4),
        "desviacion_pct": round(desviacion_pct, 2),
    }


def build_objetivos_estado(mes: date) -> dict:
    hoy = date.today()
    days_in_month = calendar.monthrange(mes.year, mes.month)[1]
    dias_transcurridos = (
        min(hoy.day, days_in_month)
        if (hoy.year == mes.year and hoy.month == mes.month)
        else days_in_month
    )
    return {
        "objetivo_kwh": None,
        "promedio_vecinos_kwh": None,
        "n_vecinos": 0,
        "diferencia_pct": None,
        "dias_transcurridos": dias_transcurridos,
        "dias_objetivo_consumidos": None,
        "texto_dinamico": "sin_objetivo",
        "excedente_kwh": None,
        "consumo_diario_real_kwh": None,
        "consumo_diario_objetivo_kwh": None,
        "consumo_acumulado_kwh": None,
        "consumo_promedio_diario_kwh": None,
    }


def build_objetivos_sugerido(conn: sqlite3.Connection, sid: str, mes: date) -> dict:
    vecinos = get_vecinos(conn, sid)
    n = len(vecinos)
    if n < MIN_VECINOS:
        return {"valor_kwh": None, "n_vecinos": n, "sin_datos": True}

    _, last_day = calendar.monthrange(mes.year, mes.month)
    totals = [
        sum(kwh for _, kwh in vs)
        for vid in vecinos
        if (vs := get_serie(conn, vid, mes, mes.replace(day=last_day)))
    ]
    if len(totals) < MIN_VECINOS:
        return {"valor_kwh": None, "n_vecinos": n, "sin_datos": True}

    return {
        "valor_kwh": round(sum(totals) / len(totals), 2),
        "n_vecinos": n,
        "sin_datos": False,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"DB no encontrada en {DB_PATH}. Corré desde la raíz del proyecto.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    fixtures: dict[str, object] = {
        "home": build_home(conn, SUMINISTRO_ID, MES),
        "diario": build_diario(conn, SUMINISTRO_ID),
        "comparacion": build_comparacion(conn, SUMINISTRO_ID, MES),
        "detalle-dia": build_detalle_dia(conn, SUMINISTRO_ID),
        "anomalia": build_anomalia(conn, SUMINISTRO_ID, MES),
        "objetivos-estado": build_objetivos_estado(MES),
        "objetivos-sugerido": build_objetivos_sugerido(conn, SUMINISTRO_ID, MES),
        "factura": {"fecha_vencimiento": None},
    }

    for name, data in fixtures.items():
        path = OUT_DIR / f"{name}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  OK {path}")

    conn.close()
    print(f"\nFixtures escritas en {OUT_DIR}/")
    print("Recordá commitear frontend/public/mock-data/ para que GitHub Actions pueda buildear.")


if __name__ == "__main__":
    main()
