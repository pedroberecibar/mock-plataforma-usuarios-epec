# Estado de Sesión Actual

## Última sesión
- **Fecha:** 2026-06-17
- **Qué se completó:** Sprint 3 completo — backend + frontend.
  - **Backend:**
    - `src/domain/proyeccion.py` — dataclass `ProyeccionMensual` (frozen)
    - `src/domain/ports/proyeccion_repository.py` — puerto `ProyeccionRepository`
    - `src/infrastructure/fakes/proyeccion_repository.py` — `FakeProyeccionRepository`
    - `src/infrastructure/sqlite/proyeccion_repository.py` — `SQLiteProyeccionRepository` (upsert + get)
    - `src/infrastructure/sqlite/models.py` — `rango_inferior_kwh` y `rango_superior_kwh` ahora `Mapped[float | None]`
    - `src/infrastructure/sqlite/vecinos_repository.py` — implementado con bounding box SQL + Haversine Python puro
    - `src/application/use_cases/calcular_proyeccion_mensual.py` — cascade 4 métodos: interanual/estacional/reciente/insuficiente
    - `src/application/use_cases/obtener_home.py` — `ObtenerHomeUseCase` + dataclasses `HomeData`, `ConsumoMes`, `ComparacionZona`
    - `src/interface/home_router.py` — `GET /home/{suministro_id}?mes=YYYY-MM`
    - `src/interface/dependencies.py` — agregado `get_vecinos_repo`, `get_proyeccion_repo`
    - `src/main.py` — cableado con `SQLiteVecinosRepository`, `SQLiteProyeccionRepository`, `home_router`
  - **Tests backend:** 138 tests pytest verdes (47 nuevos)
  - **Frontend:**
    - `frontend/src/api/types.ts` — tipos `HomeResponse`, `ProyeccionResponse`, `ConsumoMesResponse`, `ComparacionZonaResponse`
    - `frontend/src/api/home.ts` — `fetchHome(token, suministroId, mes)`
    - `frontend/src/components/BloqueConsumoMes.tsx` — total kWh + chips delta
    - `frontend/src/components/BloqueZona.tsx` — comparación con vecinos
    - `frontend/src/components/BloqueProyeccion.tsx` — rango proyectado o "insuficiente"
    - `frontend/src/components/BloqueAccesos.tsx` — links a consumo + botones griseados
    - `frontend/src/pages/HomePage.tsx` — página Home que fetcha y compone los 4 bloques
  - **Tests vitest:** 36/36 verdes (23 nuevos)
  - **Build TypeScript:** tsc + vite build limpios
  - **ruff check + format:** limpio
  - **mypy:** limpio (48 archivos)

- **Qué quedó incompleto:** —
- **Decisiones técnicas no documentadas:**
  - El threshold para "interanual" es ≥20 días en el mismo mes del año anterior (no 28).
  - El threshold para "estacional" requiere ≥20 días por año histórico, en hasta 5 años hacia atrás.
  - La proyección estacional toma el promedio de totales mensuales históricos (no ajusta por días del mes actual).
  - El ORM `ProyeccionMensual.rango_*` es nullable — requiere una migración Alembic antes de deploy en producción.
  - La implementación de `ObtenerHomeUseCase._calcular_zona` usa `mes_fin = primer_día + último_día_del_mes` para la ventana de vecinos (mismo período completo del mes, no solo días transcurridos).
- **Primer paso para la próxima sesión:** Crear migración Alembic para la columna nullable en `proyeccion_mensual`; luego Sprint 4 (autenticación real + factura/alertas).
- **Tests fallando intencionalmente:** Ninguno.

## Estado del repo
- Rama: main. Sin commitear: Sprint 3 completo (25 archivos nuevos, 6 modificados).
- Commits recientes:
  - `2777328 fix(frontend): vitest 13/13 verde + build TypeScript limpio`
  - `3ef70f2 feat(sprint-2): frontend scaffold React+Vite+Recharts con tests escritos`
  - `2460699 feat(sprint-2): Módulo Consumo M2 — backend completo`
