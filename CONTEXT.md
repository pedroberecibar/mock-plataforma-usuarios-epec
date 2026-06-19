# Estado de Sesión Actual

## Última sesión
- **Fecha:** 2026-06-19
- **Qué se completó:**
  - **Sprint 9 — Drill-down Consumo (CU-C02) + Alerta Vencimiento (CU-F05)** commiteado en `e902c31`
  - **GetDetalleDiaUseCase** (`src/application/use_cases/get_detalle_dia.py`):
    kwh_dia + kwh_mismo_dia_anio_ant (364 días atrás = mismo día-semana) + kwh_promedio_zona (None si n<5, Ley 25.326)
  - **GET /consumo/{id}/dia?fecha=YYYY-MM-DD** — sin auth, usa consumo_repo + vecinos_repo
  - **PanelDetalleDia.tsx** — componente con 3 tarjetas (este día / año ant / zona), testeable sin Recharts
  - **ConsumoPage.tsx** — click en barra → `handleClickBarra` → fetchDetalleDia → PanelDetalleDia
  - **FacturaSourceReader port** (`src/domain/ports/factura_source_reader.py`) con `FacturaResult(fecha_vencimiento)`
  - **FakeFacturaSourceReader** devuelve `date.today() + timedelta(days=5)` por defecto
  - **EvaluarVencimientoUseCase** (`src/application/use_cases/evaluar_vencimiento.py`):
    si fecha_vcto=None o días>5 → no hace nada; si días≤5 → delega a EvaluarAlertasUseCase tipo `vencimiento_proximo`
  - **POST /alertas/evaluar-vencimiento** — fire-and-forget desde FacturaPage al montar
  - **GET /factura/datos** — devuelve `FacturaDatosResponse(fecha_vencimiento)` autenticado
  - **FacturaPage.tsx** — banner amarillo (`role=alert`, `data-testid=banner-vencimiento`) cuando días≤5
  - **Fix pre-existente**: AppShell.test.tsx — etiqueta "Configuración" corregida a "Alertas"
  - **Tests**: 247 backend (+7) · 74 frontend (+13) · mypy ok · ruff ok · tsc ok · arch ok

- **Qué quedó incompleto:** —

- **Decisiones técnicas no documentadas:**
  - `kwh_mismo_dia_anio_ant` usa `fecha - timedelta(days=364)` (52 semanas) para preservar día-de-semana
  - `GetDetalleDiaUseCase` no extiende el port `ConsumoDiarioRepository` — reutiliza `get_serie(id, fecha, fecha)`
  - `FakeFacturaSourceReader` wired en main.py con default de 5 días; no hay Oracle adapter para factura aún
  - `fetchDetalleDia` en consumo.ts no pasa auth header (endpoint no requiere auth, consistente con spec)
  - Test de AppShell.test.tsx tenía "Configuración" hardcodeado; el nav real siempre fue "Alertas" (M pre-sprint)

- **Primer paso para la próxima sesión:** Sprint 10 — definir siguientes historias de usuario

- **Tests fallando intencionalmente:**
  - `tests/application/use_cases/test_evaluar_alertas.py::test_registra_envio_en_notificaciones_enviadas`
    (falla pre-existente desde sprint 7, no relacionada con sprint 9)

## Estado del repo
Commits recientes:
- e902c31 feat(sprint-9): drill-down consumo y alerta vencimiento factura
- c346e7a fix(auth): auto-logout cuando el JWT expira en ObjetivosPage
- 3649bab feat(sprint-8): objetivo sugerido, onboarding primer login e indicadores O1-O3
- 4b740f2 feat(sprint-7): barra de progreso, alerta objetivo superado y seed contraseñas
- d974e6f feat(sprint-6): auth argon2id, cerrar sesión y objetivos de consumo
