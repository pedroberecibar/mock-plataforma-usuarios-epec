# Estado de Sesión Actual

## Última sesión
- **Fecha:** 2026-06-25
- **Rama:** `spike/oracle-perfiles-georef`
- **Qué se completó:**
  - **Hero strip + saludo usuario:** `HeroSaludo.tsx` (h1 Space Grotesk 40px, pills de tarifa/suministro con `font.mono`), `GET /auth/me` endpoint, `AuthState` extendido con `nombre` y `nroSuministro`, `LoginResponse` devuelve nombre, `fetchPerfil` en frontend
  - **Strategy pattern completo:** `SuministroIngestionStrategy` (puerto), `ClouStrategy`, `NansenStrategy`, `ChupeteStrategy`, `SigecBaseStrategy`, `IngestionStrategySelector`, `OracleSuministroMetaReader`, `PoblarSuministroUseCase`, `SQLiteVecinosCacheRepository`, `POST /ingest/poblar`
  - **Fix _DIAS_HISTORICO:** 90 → 400 días (cubre año anterior completo para comparación interanual)
  - **Fix crítico suministro_id mismatch:** `SigecBaseStrategy._fetch_sync` usaba `row.srv_codigo` (Oracle raw `'2817670'`) en vez del canónico `'SRV-2817670'`. Fix: pasar `srv_codigo` canónico como parámetro y usarlo en `LecturaTelemedida`
  - **Fix frescura en PoblarSuministroUseCase:** si `get_ultima_fecha(suministro_id)` devuelve fecha de ayer o hoy → saltear ingesta Oracle (evita query pesada en cada login)
  - **Fix Vite proxy:** `/ingest` faltaba en `frontend/vite.config.ts` — requests a `/ingest/poblar` caían al servidor Vite y fallaban silenciosamente
  - **Limpieza SQLite dev:** 540 filas huérfanas bajo `'2817670'` eliminadas de `consumo_diario` y `suministros`
  - **339 tests en verde**
- **Qué quedó incompleto:**
  - Cambios NO commiteados (ver git status abajo) — hay una cantidad grande de archivos modificados y nuevos
  - Validación end-to-end en browser del fix de suministro_id (Vite proxy recién corregido, pendiente reinicio de Vite y nuevo login)
  - Análisis del cálculo de promedio de consumo de vecinos (próxima tarea)
- **Decisiones técnicas no documentadas:**
  - `PoblarSuministroUseCase` usa `session_factory` propio (no el del request context de FastAPI) porque se ejecuta como `BackgroundTask` después de que el request ya cerró
  - Frescura definida como ≤1 día: si `ultima_fecha >= ayer` → no re-ingestar. Ajustable si se necesita otro umbral
  - `SigecBaseStrategy.leer_lecturas` recibe `srv_codigo` canónico pero no lo pasa a la query Oracle — solo lo usa como clave de almacenamiento. La query Oracle sigue usando el `medidor` (equipo físico).
- **Primer paso para la próxima sesión:** Reiniciar Vite y validar en browser que los datos de Oracle aparecen en el inicio. Luego analizar el cálculo de promedio de vecinos.
- **Tests fallando intencionalmente:** Ninguno

## Estado del repo
```
Branch: spike/oracle-perfiles-georef
Sin commit: ~23 archivos modificados + ~12 archivos nuevos (ver git status)
Commits recientes:
6209180 feat(vecinos): subestación-based neighbor calculation via GEOREF.VW_INTELIGENTES
a87cf3b spike: script exploración Oracle perfiles georef (solo lectura)
d9d918e feat(sprint-11): consumo horario + hora pico — stack completo
5b3ff33 fix(ui/consumo): cards vecinos sin borde, shadow.sm, radius.lg
a592ea7 feat(ui/consumo): grid de 2 filas con cards estilo inicio
```
