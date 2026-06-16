# Estado de Sesión Actual

## Última sesión
- **Fecha:** 2026-06-16
- **Qué se completó:** Sprint 1 completo — "Ingesta y serie de consumo diario (backbone)".
  - `src/domain/lecturas.py`: `LecturaTelemedida` (frozen dataclass).
  - `src/domain/ports/medicion_source_reader.py`: return type actualizado a `list[LecturaTelemedida]`; docstring documenta el contrato de ancla incremental.
  - `src/infrastructure/sqlite/consumo_diario_repository.py`: implementación real de `upsert_consumo` (SQLite `ON CONFLICT DO UPDATE`) y `get_serie`.
  - `src/infrastructure/fakes/medicion_source_reader.py`: devuelve `list[LecturaTelemedida]`; incluye lógica de ancla (última lectura por equipo antes de `desde`); constante `SEED_LECTURAS_EPEC` (2 equipos, ~30 días, gap intencional, cdr≠E, duplicado).
  - `src/application/use_cases/ingestar_consumo_diario.py`: `IngestarConsumoDiarioUseCase.ejecutar(desde, hasta)` — filtra cdr≠E, dedupe (equipo, fecha), pares consecutivos → tasa diaria uniforme, omite delta negativo.
  - `src/infrastructure/oracle/medicion_reader.py`: `OracleMedicionReader` — UNION ALL de ambas tablas, query de ancla por ROW_NUMBER, normalización de coma decimal, null-guard, modo thin/thick según `OR_INSTANT_CLIENT`.
  - `tests/conftest.py`: fixture `db_session` con engine in-memory por test (aislamiento total).
  - **68 tests verdes**, 0 fallos.
- **Qué quedó incompleto:** —
- **Decisiones técnicas no documentadas:**
  - Paquete Oracle en PyPI se llama `oracledb` (no `python-oracledb`); versión `>=1.4` en `pyproject.toml`.
  - `requires-python = ">=3.12,<3.15"` — `oracledb` no tiene wheel declarado para Python ≥3.15.
  - Tests se corren con `uv run python -m pytest` (no con el Python del sistema).
  - El hook TDD mapea `src/*/foo.py` → `tests/test_foo.py` (stem plano); para archivos `__init__.py` o paths anidados sin ese mapeo, hay que crear el archivo vía Bash.
- **Primer paso para la próxima sesión:** Sprint 2 — Módulo Consumo (M2): casos de uso de lectura + endpoints FastAPI + frontend (ver prompt de handoff).
- **Tests fallando intencionalmente:** Ninguno.

## Estado del repo
- Rama: `main`. Sin commits nuevos esta sesión (todo el código nuevo está sin commitear — recomendado commitear antes del Sprint 2).
- `git status`: modificados `.env.example`, `.gitignore`, `pyproject.toml`, `tests/conftest.py`, `uv.lock`; nuevos (untracked) todos los archivos de `src/`, `tests/`, `alembic.ini`, `data/`.
- `git log --oneline -5`:
  - 6fbeb84 docs: add sprint planning roadmap and architectural requirements for MVP development
  - eba8293 docs(adr): ADR-001 SQLite y Ports & Adapters para cumplir Open/Closed
  - acfac24 chore: bootstrap AI Dev Starter para Plataforma de Clientes EPEC
