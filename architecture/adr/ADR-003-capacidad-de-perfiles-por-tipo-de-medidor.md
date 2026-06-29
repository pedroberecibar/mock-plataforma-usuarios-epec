# ADR-003 — Capacidad de perfiles (15 min) por tipo de medidor

**Fecha:** 2026-06-29
**Estado:** Aceptado
**Decisores:** Pedro Berecibar (owner) — Plataforma de Clientes EPEC

---

## Contexto

**Realidad de negocio:** por problemas de infraestructura y comunicación SCADA de los
medidores **NANSEN**, EPEC **no puede obtener sus perfiles** (mediciones cada 15 min).
Los medidores **CLOU sí** exponen perfiles. Es un problema temporal de infra: cuando se
resuelva, se podrá ingestar perfiles NANSEN sin rediseñar la app.

Para soportar esa evolución se introdujo el patrón **Strategy** de ingesta
(`SuministroIngestionStrategy` + selector por `telemedible`: CLOU / NANSEN / CHUPETE).

**Diagnóstico read-only (2026-06-29, Fase 0) — corrige supuestos previos:**
- La query horaria CLOU/SIGEC **funciona**: sobre 2025-01-01→hoy devolvió 43.444 lecturas
  horarias de 179 suministros CLOU. Los perfiles CLOU están disponibles.
- El medidor NANSEN (91013486 / suministro 2817670) participa del lote pero aporta **0**
  lecturas horarias — no genera error, simplemente no tiene perfiles.
- El `ORA-01722` visto en el scheduler **no es reproducible**: fue transitorio y el
  scheduler ya lo captura y reintenta. **No** lo dispara NANSEN ni el tamaño del lote.

**Gaps del Strategy actual (auditoría):**
1. El patrón modela la ingesta **diaria**, no la capacidad de **perfiles**. Las 3
   estrategias son hoy idénticas (heredan `SigecBaseStrategy`, solo difieren en `nombre`).
2. La ingesta **horaria** (`OracleMedicionHorariaReader`) es un camino **paralelo** que no
   pasa por el Strategy. Cuando EPEC habilite NANSEN, habría que tocar ese camino, no una
   estrategia → leak respecto del objetivo Open-Closed.
3. La capacidad **no se persiste**: `meta.telemedible` se resuelve en
   `PoblarSuministroUseCase` pero no se guarda en `suministros`. Por eso la app **no puede
   avisarle** al usuario que su medidor solo da granularidad diaria.
4. (Menor) `SigecBaseStrategy.leer_lecturas` traga todas las excepciones devolviendo `[]`.

## Decisión

**Elegimos:** modelar **"soporta perfiles" (`soporta_perfiles: bool`)** como capacidad del
tipo de medidor, parte de la abstracción de estrategia, y consultarla en ingesta,
persistencia y presentación.

**Porque:** el valor durable no es tapar el `ORA-01722` (transitorio, ya contenido) sino la
feature de negocio: **distinguir CLOU (con perfiles) de NANSEN (solo diario) y avisar al
usuario**. Modelar la capacidad en la estrategia hace que habilitar NANSEN en el futuro sea
un cambio localizado (`NansenStrategy`), sin tocar casos de uso ni UI (Open-Closed).

Concretamente:
- **Estrategia (dominio):** `soporta_perfiles: bool` en el puerto. CLOU=`True`,
  NANSEN=`False`, CHUPETE=`False`. Extensión futura: método `leer_perfiles(...)` que
  NANSEN implementará cuando haya fuente (hoy YAGNI).
- **Persistencia:** columna `suministros.telemedible`; `PoblarSuministroUseCase` la guarda.
- **Presentación:** la API expone `soporta_perfiles`; el frontend muestra el perfil horario
  (CLOU) o un **aviso** "tu medidor NANSEN solo permite análisis diario; los perfiles
  estarán disponibles cuando EPEC resuelva la infraestructura" (NANSEN).
- **Ingesta horaria (optimización, no bugfix):** el scheduler puede filtrar el lote a
  equipos con `soporta_perfiles` para no consultar en vano a los NANSEN. Baja prioridad: el
  `ORA-01722` transitorio ya lo absorbe el try/except del scheduler.

## Alternativas consideradas

| Opción | Pros | Contras | Por qué se descartó |
|--------|------|---------|---------------------|
| No modelar capacidad; confiar en `null` de hora-pico | Cero cambios | No distingue "NANSEN sin perfiles" de "CLOU sin datos aún"; no se puede avisar | No cumple el requisito de negocio (aviso al usuario) |
| Hack en la query horaria (castear/saltear no-numéricos) | Rápido | Tapa un síntoma transitorio; no modela la realidad de negocio | No aporta la capacidad ni el aviso |
| Capability en la estrategia + persistir + exponer (elegida) | Open-Closed real; habilita el aviso; futuro NANSEN localizado | Requiere migración + tocar 4 capas | — |

## Consecuencias

**Positivas:**
- El usuario NANSEN entiende por qué solo ve análisis diario (transparencia).
- Habilitar perfiles NANSEN en el futuro = implementar `leer_perfiles` + flip del flag en
  `NansenStrategy`. Cero cambios en use cases/UI.
- La capacidad queda como concepto de dominio único, consultable por ingesta y UI.

**Negativas / trade-offs:**
- Migración de esquema (`suministros.telemedible`) + backfill.
- El flag duplica conceptualmente lo que ya sabe el selector; se acepta para poder
  persistir/exponer sin reconsultar Oracle en cada request.

**Riesgos:**
- Que el `telemedible` persistido quede desactualizado si un medidor cambia de tipo.
  Mitigación: poblar lo re-escribe en cada ingesta (upsert).

## Plan de implementación (fases, TDD)

- [x] **Fase 0** — Diagnóstico read-only (2026-06-29). Hallazgos arriba.
- [ ] **Fase 1** — `soporta_perfiles: bool` en el puerto + 3 estrategias + tests.
- [ ] **Fase 2** — (opcional) filtrar el lote horario a equipos con `soporta_perfiles`.
- [ ] **Fase 3** — Migración `suministros.telemedible` + persistir en poblar + backfill 2817670.
- [ ] **Fase 4** — Exponer `soporta_perfiles` por la API (`/cuenta`).
- [ ] **Fase 5** — UI: aviso NANSEN + gating del perfil horario (TDD + validación browser).
- [ ] **Fase 6** — (futuro EPEC) `NansenStrategy.leer_perfiles` + flip del flag.

Orden de valor: 1 → 3 → 4 → 5 (la feature de aviso). La Fase 2 es optimización aparte.
