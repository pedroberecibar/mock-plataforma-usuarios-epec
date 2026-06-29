# ADR-002 — Entornos de despliegue y fuentes de datos

**Fecha:** 2026-06-29
**Estado:** Aceptado
**Decisores:** Pedro Berecibar (owner) — Plataforma de Clientes EPEC

---

## Contexto

Una auditoría de fiabilidad (2026-06-29) detectó que la plataforma mostraba **datos
sintéticos como si fueran reales**. Las causas:

1. `scripts/seed_demo.py` genera consumo inventado con `random.uniform()` (modelo
   estacional + ruido) y lo escribe **en la misma DB que sirve el backend**
   (`data/plataforma_clientes.db`). De los 16 usuarios de login, 10 tenían consumo
   100 % sintético y el perfil horario era sintético para 15 de 16.
2. El fallback `FakeFacturaSourceReader` devuelve una deuda hardcodeada
   (`$12.345,67`) cuando Oracle no está configurado.
3. La demo pública de GitHub Pages (rama `mock-platform`) servía una mezcla de
   fixtures, sin distinción clara entre lo real y lo inventado.

La lógica de cálculo del backend es correcta y conservadora (los casos de uso
devuelven `null` cuando falta dato, nunca rellenan), pero **la fuente de datos
estaba contaminada**. Ver el análisis completo que originó esta ADR.

Restricciones duras del entorno:

- **Oracle (`PRODEBS_SEE`) es interno de EPEC** (`epec2-scan2`, read-only validado por
  jefatura). **No es accesible desde GitHub Actions ni desde GitHub Pages.**
- GitHub Pages es **hosting estático**: no hay backend ni conexión a Oracle en runtime.
- El owner quiere ser **usuario #1** (dogfooding) de su propio suministro `2817670`
  (Palacios N., medidor NANSEN) para analizar su consumo y detectar mejoras directo.

## Decisión

**Elegimos:** separar la plataforma en **dos entornos con un único origen de datos
(Oracle)**, erradicando todo dato sintético de las rutas que ve un usuario.

**Porque:** la confiabilidad es un requisito de producto, no un detalle. "Estático"
(forma de entrega) no es lo mismo que "sintético" (origen inventado): la demo puede
ser estática y a la vez 100 % real si sirve un *snapshot* de datos reales.

### Entorno A — Desarrollo (`main` + ramas de feature/fix)

- **Origen:** Oracle `PRODEBS_SEE`, read-only. Único origen de verdad.
- **Stack:** backend FastAPI + SQLite como **cache** ingestada de Oracle (ver ADR-001).
- **Datos:** reales y procesados por los casos de uso. **Cero dato sintético.**
- **Usuarios reales = los suministros que ingestamos** (`INGEST_EQUIPOS` + vecinos por
  subestación). Ampliar usuarios = ampliar la ingesta, **nunca** sembrar consumo.
- `main` se mantiene estable y funcional; se ramifica para features/fixes (GitHub Flow).

### Entorno B — Demo portfolio (rama `mock-platform`, GitHub Pages)

- **Origen:** Oracle → **snapshot** del suministro real `SRV-2817670`.
- **Stack:** build estático de React (`vite.config.gh-pages.ts` aliasa `api/*` → `mock/*`),
  servido desde GitHub Pages. Sin backend.
- **Datos:** snapshot real de 2817670 generado por `scripts/generate_mock_fixtures.py`
  hacia `frontend/public/mock-data/*.json` (commiteado). Real, solo que congelado.
- **Usuario único:** Palacios / 2817670 (`frontend/src/mock/auth.ts`).
- **Privacidad:** de los vecinos solo se publican **agregados ≥5** (`promedio`,
  `n_vecinos`), nunca consumo individual ni IDs. Invariante a sostener.

### Reglas transversales (las 6 decisiones)

1. **Oracle es la única fuente de verdad.** Ningún número visible puede originarse en
   `random`/fixtures inventados.
2. **`main` no contiene datos sintéticos.** La DB real solo recibe ingesta de Oracle.
3. **Conjunto de usuarios reales = suministros ingestados** (palanca: `INGEST_EQUIPOS` /
   ingesta on-demand). Nunca un seed.
4. **La demo = snapshot real de 2817670**, regenerado a demanda y commiteado.
5. **Privacidad:** demo pública solo publica agregados de vecinos (≥5), nunca individual.
6. **Sin factura fake en `main`:** `FakeFacturaSourceReader` se reemplaza por un 503
   explícito (igual que medición/cuenta cuando Oracle no está configurado).

### Decisiones operativas cerradas

- **`seed_demo.py` → quarantine.** Se conserva solo para desarrollo de UI offline sin
  Oracle, con un **guard que aborta si `DATABASE_URL` apunta a la DB real**; solo puede
  escribir en una DB descartable (ej. `data/ui-dev.db`). La DB real nunca recibe consumo
  `random`.
- **Refresh de la demo = comando manual único.** Un script/target (ej. `refresh-demo`)
  que, en la máquina del owner (la única con acceso a Oracle): ingesta 2817670 fresco →
  regenera fixtures → commitea. El push a `main` dispara `deploy-demo.yml`
  (build `build:demo` → publica a `mock-platform`). **CI no regenera fixtures** porque no
  alcanza Oracle.

## Alternativas consideradas

| Opción | Pros | Contras | Por qué se descartó |
|--------|------|---------|---------------------|
| Mantener `seed_demo.py` sembrando la DB real | Demo multi-usuario rica sin Oracle | Muestra consumo inventado como real; rompe confiabilidad | Es exactamente el problema que origina esta ADR |
| Demo con datos 100 % sintéticos (sin dato real) | Cero dependencia de Oracle; sin tema de privacidad | El owner no puede dogfoodear su consumo real | Pierde el objetivo de ser usuario #1 |
| Backend live para la demo (no estático) | Datos siempre frescos | GitHub Pages no tiene backend; Oracle es interno e inaccesible desde la nube | Inviable por la red de EPEC |
| Snapshot real de 2817670 en demo estática (elegida) | Real + dogfooding + sin exponer backend ni Oracle | Snapshot congelado (requiere refresh manual) | — |

## Consecuencias

**Positivas:**
- Lo que ve un usuario en `main` es real y trazable a Oracle.
- El owner es usuario #1 de su propio consumo, en una URL pública de portfolio.
- La frontera real/snapshot queda explícita y enforced, no implícita.

**Negativas / trade-offs aceptados:**
- La demo muestra datos con cierta latencia (snapshot manual, no live).
- El refresh depende de la máquina del owner (única con acceso a Oracle).
- `seed_demo.py` sobrevive (quarantined) en vez de eliminarse: hay que mantener el guard.

**Riesgos:**
- Re-contaminación de la DB real si alguien corre el seed sin guard. **Mitigación:** guard
  por `DATABASE_URL` + (opcional) fitness test que falle ante firma de consumo `random`.
- Fuga de privacidad si un fixture publicara consumo individual de vecinos.
  **Mitigación:** `generate_mock_fixtures.py` solo emite agregados ≥5; revisar en code review.

## Estado de implementación

ADR aceptada el 2026-06-29; persiste la decisión.

**Runbook operativo del deploy de la demo (incluye los 5 bloqueos conocidos):**
`docs/RUNBOOK-deploy-mock-platform.md`.

Trabajo de implementación:
- [x] Guard de quarantine en `scripts/seed_demo.py` (`assert_safe_seed_target`, default
      `data/ui-dev.db`, aborta ante la DB real). Tests: `tests/scripts/test_seed_demo.py`.
- [x] Reemplazar `FakeFacturaSourceReader` por 503 en `src/main.py` cuando no hay Oracle.
      Test: `tests/test_main.py::test_factura_datos_returns_503_when_oracle_not_configured`.
- [x] Comando único `scripts/refresh_demo.py` (ingesta 2817670 → fixtures → instrucción de
      commit/push). Tests: `tests/scripts/test_refresh_demo.py`.
- [x] Purgar consumo sintético de `data/plataforma_clientes.db` (2026-06-29). Enfoque
      elegido: DB mínima con **un único login (2817670)** + consumo real re-ingestado de
      Oracle para 2817670 y sus **vecinos por subestación** (189). Backups:
      `plataforma_clientes.prepurga-*.db` y `*.purgado-old.db`. `consumo_horario` queda
      vacío (2817670 es NANSEN, sin perfiles de 15 min). `INGEST_EQUIPOS=91013486` en `.env`.
- [ ] (Opcional) ampliar `INGEST_EQUIPOS` para sumar usuarios reales a `main`.
- [ ] (Opcional) excluir medidores NANSEN de la ingesta horaria (hoy el scheduler loguea
      `ORA-01722` al intentar leer 15-min de 2817670; es no-fatal pero ruidoso).
- [ ] (Opcional) fitness test anti-seed-sintético.
