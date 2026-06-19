# Estado de Sesión Actual

## Última sesión
- **Fecha:** 2026-06-19
- **Qué se completó:**
  - Sprint 10: CU-C06 (anomalía z-score), CU-C07 (export CSV), CU-A06 (rate-limit cooldown por tipo)
  - fix(security): IDOR en `/consumo/anomalia` y `/consumo/export/csv` → `get_suministro_actual`
  - fix(privacidad): k-anonymity `n_vecinos < 5` en `ObtenerHomeUseCase`
  - fix(alertas): timestamp usa fecha inyectada en `EvaluarAlertasUseCase`
  - fix(encoding): strings garbled en `ObjetivosPage.tsx` (curly quotes → ASCII)
  - chore(design-system): refactor SOLORA warm cream
  - feat(factura): integración experimental API EPEC en `ObtenerLinkFacturaUseCase` (httpx)
  - refactor scheduler: backfill en una sola llamada en vez de día por día
  - Suite verde: pytest 262/262 · vitest 74/74 · mypy ok · ruff ok · tsc ok
- **Qué quedó incompleto:**
  - NFR Responsive: screenshots en 375/768/1280 — dev server no disponible en sesión
  - NFR Performance Lighthouse CI < 3 s en 3G — no medido
  - NFR PWA offline (service worker) — no implementado
  - NFR Observabilidad (structlog + Sentry) — no implementado
  - CU-A01: push web real (PywebpushSender) — solo email implementado
  - IDOR en `/consumo/{id}/diario` y `/consumo/{id}/comparacion` — pendiente menor
  - DEUDA arq.: `httpx` importado directamente en `ObtenerLinkFacturaUseCase` (viola Ports & Adapters); refactorizar a `FacturaVerificacionPort` en sprint-11
- **Decisiones técnicas no documentadas:**
  - La API de EPEC para verificar contratos es `GET https://www.epec.com.ar/api/contratos/no-ov/{nc}/{ct}` con `apikey: web-prod`. Encontrada por el usuario explorando la web de EPEC.
  - El scheduler de ingesta ahora hace una sola llamada al source reader por período (en vez de iterar día por día) — cambio de comportamiento que simplifica el code pero asume que el source soporta rangos amplios.
- **Primer paso para la próxima sesión:** Sprint 11 — refactorizar `httpx` a `FacturaVerificacionPort`, luego screenshots responsive, luego observabilidad
- **Tests fallando intencionalmente:** Ninguno

## Estado del repo
```
def7420 feat(factura): integración experimental API EPEC + refactor scheduler
b5c8516 fix(security): IDOR anomalía/CSV, encoding ObjetivosPage
f29fff5 refactor(components): add Icon wrapper
e9e312a fix(privacidad): k-anonymity n<5 ObtenerHomeUseCase
e9d31c3 feat(sprint-10): CU-C06 anomalía, CU-C07 CSV, CU-A06 rate-limit
```
Working tree limpio (solo archivos ignorables: db-shm, db-wal, epec.db, login-warm.png)
