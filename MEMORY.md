# Conocimiento Arquitectónico Acumulado

<!-- Este archivo se llena a lo largo del tiempo con decisiones técnicas, patrones descubiertos
     y lecciones aprendidas. No borrar entradas, solo agregar. Claude lo lee al iniciar sesión. -->

## Decisiones técnicas
<!-- Ejemplo:
### 2026-06-XX — Elección de Serena sobre GitNexus
- Motivo: Serena usa LSP y permite edición a nivel de símbolo, offline.
- Alternativa descartada: GitNexus (solo lectura, menos estable).
-->

### 2026-06-29 — Entornos y fuentes de datos (ADR-002)
- Único origen: Oracle `PRODEBS_SEE`. Dos entornos: `main` (backend real, cero sintético)
  y `mock-platform` (GitHub Pages, snapshot real de 2817670 vía `generate_mock_fixtures.py`).
- `seed_demo.py` quarantined (guard por `DATABASE_URL`, solo DB descartable). Factura fake → 503.
- Detalle completo: `architecture/adr/ADR-002-entornos-y-fuentes-de-datos.md`.

## Patrones establecidos
<!-- Patrones que ya se usan en el proyecto y no hay que rediscutir. -->

## Anti-patrones detectados
<!-- Cosas que probamos y salieron mal. No repetir. -->

## Dependencias críticas y versiones
<!-- Versiones exactas que sabemos que funcionan en nuestro entorno. -->
