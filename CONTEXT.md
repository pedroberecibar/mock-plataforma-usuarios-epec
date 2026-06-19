# Estado de Sesión Actual

## Última sesión
- **Fecha:** 2026-06-19
- **Qué se completó:**
  - **Sprint 11 completo** (commit `cf273a1`): FacturaVerificacionPort, IDOR /diario y /comparacion, JwtAuthProvider.autenticar, structlog, responsive screenshots
  - **Security review** (agente `security-reviewer`): ejecutado y resueltos todos los hallazgos bloqueantes
  - **Code review** (agente `code-reviewer`): ejecutado y resueltos todos los hallazgos bloqueantes
  - **Fix IDOR residual** (commit `b340146`): 4 endpoints adicionales migrados a `get_suministro_actual`:
    - `GET /consumo/dia` (antes `/{suministro_id}/dia`, sin auth)
    - `GET /home` (antes `/{suministro_id}`, token pero sin propiedad)
    - `GET /objetivos/sugerido` (antes `/sugerido/{id}`, sin auth del todo)
    - `GET /objetivos/estado` (antes `/{id}/estado`, sin auth del todo)
  - **Fix info disclosure** EPEC: `ValueError` → 422, `Exception` → 503 sin exponer internals
  - **Fix auth bypass**: `password_hash=None` rechaza login en router + provider
  - **Fix apikey**: `EPEC_API_KEY` env var (default `web-prod`)
  - **Fix assert**: `assert resultado is not None` → `HTTPException(500)`
  - **Fix tests auth**: `(401, 500)` → `401` estricto con `_make_auth_app`
  - **Fix input validation**: `numero_cliente`/`numero_contrato` validados como numéricos antes de interpolación URL EPEC
  - **Suite:** 271 pytest · 74 vitest · mypy ok · ruff ok · tsc ok · hooks ok
  - **Commits:** `b340146`, `6997f6d`
- **Qué quedó incompleto:**
  - NFR Performance Lighthouse CI < 3 s en 3G — no medido
  - NFR PWA offline (service worker) — no implementado
  - CU-A01: push web real (PywebpushSender) — solo email implementado
  - UAT con usuarios internos
  - Sentry/OTel — solo structlog, sin Sentry
  - Rate limiting en `/auth/login` (finding MEDIO — próximo sprint)
  - JWT revocación/duración (finding BAJO — próximo sprint)
  - structlog scrubbing de campos sensibles (finding INFO — próximo sprint)
  - `FacturaRedireccion` tabla dead code (code review finding — próximo sprint)
  - `_configure_logging()` se ejecuta al importar `main.py` (finding INFO)
  - double-wrapping code review finding: **FALSE POSITIVE** — scheduler recibe `oracle_reader` raw (no `_non_blocking_reader`) y lo envuelve correctamente en línea 125; el `_non_blocking_reader` de `main.py:246` es instancia separada para FastAPI dep
- **Decisiones técnicas no documentadas:**
  - `password_hash=None` en `autenticar()` ahora siempre rechaza (cambia MVP donde era bypass opcional)
  - Tests de auth usan `_make_auth_app()` helper con cadena real de deps (no override directo de `get_suministro_actual`) para poder verificar 401 real
  - `EPEC_API_KEY` env var requerida en producción; si no está → usa `web-prod` como default
  - `numero_cliente`/`numero_contrato` validados como `^\d+$` — contratos con letras serán rechazados
- **Primer paso para la próxima sesión:** Handoff sprint-12 o UAT con usuarios internos. Si se hace handoff: correr `/handoff` para generar prompt del próximo agente.
- **Tests fallando intencionalmente:** Ninguno

## Estado del repo
```
6997f6d fix(security): validación de inputs EPEC + tests auth estrictos (401 no 500)
b340146 fix(security): IDOR residual + info disclosure + auth bypass + apikey
cf273a1 feat(sprint-11): producción — FacturaVerificacionPort, responsive, observabilidad, security
4fe34c5 chore(context): actualizar CONTEXT.md para handoff sprint-11
def7420 feat(factura): integración experimental con API EPEC + refactor scheduler backfill
```
Working tree limpio (untracked: db-shm, db-wal, epec.db, login-warm.png, screenshots/)
```
