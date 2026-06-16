# Estado de Sesión Actual

<!-- Claude actualiza este archivo al final de cada sesión con /end-session.
     Al iniciar, /start-session lo lee para retomar exactamente donde quedó. -->

## Última sesión
- **Fecha:** 2026-06-16
- **Qué se completó:** Bootstrap del AI Dev Starter sobre el proyecto **Plataforma de Clientes EPEC**. Se copió la estructura del starter preservando los docs existentes de EPEC (Design System, prompts de Stitch), se inicializó git, se definió el stack en `CLAUDE.md` (FastAPI + React/TS + PostgreSQL), se arreglaron los hooks de Claude (`tdd_workflow.py` y `capture_decision.py` ahora leen el JSON de stdin), se adaptó `lefthook.yml`/`pyproject.toml`/`package.json` al stack y se instalaron las dependencias Python con `uv`.
- **Qué quedó incompleto:**
  - `npm install` falla por el proxy TLS corporativo (`ERR_SSL_CIPHER_OPERATION_FAILED`) → **lefthook y commitlint no están instalados**, por lo que los git hooks locales aún no corren. Resolver cuando haya red sin proxy o pedir binarios al equipo.
  - `VAULT_PATH` sin completar en `.env` (necesario para el MCP de Obsidian y `capture_decision.py`).
  - Frontend React/TS y backend FastAPI todavía sin scaffoldear (`src/` solo tiene README).
- **Decisiones técnicas no documentadas:**
  - Se quitó `archunit` del `pyproject` (no existe en PyPI; los tests de arquitectura usan `ast` puro).
  - Dev deps migradas de `optional-dependencies` a `[dependency-groups]` (lo que espera `uv sync --dev`).
  - `package = false` en `[tool.uv]` (es una app, no una librería empaquetable).
  - Secret scanning (trufflehog/secretlint) se deja solo en CI, no en pre-commit, para no romper commits offline.
- **Primer paso para la próxima sesión:** Completar `VAULT_PATH` en `.env`, resolver la instalación de lefthook/commitlint (proxy), y empezar a scaffoldear el backend FastAPI bajo `src/` siguiendo TDD.
- **Tests fallando intencionalmente:** Ninguno. (Los tests de arquitectura quedan en `skipped` hasta que exista código en `src/`.)

## Estado del repo
<!-- Claude actualiza esta sección con `git status` y `git log --oneline -5` -->
- Repositorio inicializado en rama `main`. Primer commit con el scaffold del starter adaptado a EPEC.
