# Plan de Sprints — MVP Plataforma de Clientes EPEC

> Derivado de la página de producto "Plataforma clientes EPEC" (Notion), el
> [Plan de arquitectura — MVP](https://app.notion.com/p/38162e87552181a288c2c9f9cd776ce9)
> y `docs/adr/` (ADR-001: SQLite + Ports & Adapters).
> Fecha de elaboración: 2026-06-16.

## Alcance del MVP (lo que entra)

5 módulos + pipeline de datos, **siempre en kWh, sin montos, sin banda horaria,
sin subsidio, sin Cortes/Reclamos**:

| Módulo | Núcleo (Must) |
|---|---|
| **M1 — Home** | Consumo del mes (vs. año anterior y vs. mes anterior), Comparación con tu zona, Proyección al cierre (rango), Accesos directos a factura, Timestamp |
| **M2 — Consumo** | Barras diarias, drill-down mes→día, todo en kWh, comparación histórica, transparencia de latencia |
| **M3 — Mi Factura** | Explicación de conceptos *sin montos*, botón de redirección a EPEC (link con Nº cliente + Nº contrato, 2 inputs manuales), alertas de vencimiento |
| **M4 — Alertas** | Push configurable (factura disponible / vencimiento / consumo anómalo), config granular, email complementario, rate-limit |
| **M6 — Objetivos** | Objetivo sugerido (promedio vecinos 150 m, mismo mes año anterior), seteo en primer login, edición, 3 indicadores |

**Should** (se difieren a hardening): detección de consumo anómalo (M2),
export CSV (M2), email complementario y rate-limit (M4).

## Supuestos del plan (ajustables)

- **Sprints de 2 semanas**, equipo chico (1-2 devs full-stack). Si cambia el
  tamaño/duración, se reordena.
- TDD obligatorio (RED→GREEN→REFACTOR) y Ports & Adapters por capa en **cada**
  historia: puerto en `domain`, caso de uso en `application` testeado con
  *fakes* in-memory, adapter concreto en `infrastructure`, router en `api`.
- Oracle EPEC se accede solo-lectura detrás de `MedicionSourceReader`; mientras
  no haya credenciales/VPN se trabaja con un adapter *fake* + dataset semilla.

## Dependencia central (define el orden)

La **serie de consumo diario `c(d)`** es la base de todo: Home, Consumo,
anomalías, proyección y objetivos dependen de ella. El **cálculo de vecinos en
150 m** es compartido por *Comparación con tu zona* (M1) y *objetivo sugerido*
(M6) → se construye una vez y se reutiliza.

```
S0 Cimientos ──► S1 Ingesta/serie c(d) ──┬─► S2 Consumo (M2)
                                          ├─► S3 Proyección + Home (M1) ──► S4 Objetivos (M6)
                                          └─► S5 Factura + Notificaciones (M3+M4)
                                                                              └─► S6 Hardening + NFR + Should
```

---

## Sprint 0 — Cimientos (habilitador, sin features de negocio)

**Meta:** esqueleto hexagonal que compila, testea y despliega; desbloquear el entorno.

- Estructura `app/domain · application · infrastructure · api` + composition root (`api/dependencies.py`).
- Declarar los **7 puertos** como `abc.ABC` vacíos: `ConsumoDiarioRepository`, `ObjetivoConsumoRepository`, `VecinosRepository`, `MedicionSourceReader`, `TaskQueue`, `NotificationSender`, `AuthProvider`.
- Esquema DB inicial (Alembic) de las tablas del Plan de arquitectura (§5) + adapters SQLite vacíos y *fakes* in-memory.
- Test de arquitectura en CI (AST puro): domain no importa infra; ningún caso de uso importa sqlite/oracle/redis/jwt.
- `AuthProvider` con `JwtAuthProvider` mínimo (login stub) — auth real queda como punto abierto.
- Frontend: scaffold Next.js + Tailwind/shadcn + TanStack Query + esqueleto PWA + layout responsive (viewport móvil de referencia).
- **Desbloquear:** resolver `npm install` (proxy TLS) o pedir binarios; completar `VAULT_PATH`.

**DoD:** `pytest` y CI verdes con el árbol vacío, frontend levanta, swap fake↔SQLite se hace solo tocando el composition root.

## Sprint 1 — Ingesta y serie de consumo diario (backbone)

**Meta:** poblar `consumo_diario` desde la fuente EPEC. Desbloquea todo lo demás.

- `MedicionSourceReader` → `OracleMedicionReader` (python-oracledb thin) **+ fake con dataset semilla**.
- ETL (puerto `TaskQueue` → `CeleryTaskQueue`): `UNION ALL` de `XXCO_LECTURAS_TELEMEDIDAS`(_H), dedupe por (equipo, cdr, fecha), filtro `cdr_codigo='E'`, normalizar coma decimal.
- Reconstrucción de la serie diaria `c(d)` (tasa entre lecturas consecutivas, pasos 1-2 de la Especificación técnica).
- `ConsumoDiarioRepository` SQLite (`upsert` idempotente) + persistencia.

**DoD:** corriendo el job sobre el dataset semilla, la serie diaria queda materializada y verificada por tests con el *fake* (sin Oracle real).

## Sprint 2 — Módulo Consumo (M2) — *CU-C01..C05*

**Meta:** primera pantalla con datos reales end-to-end.

- Casos de uso de lectura de serie y comparación histórica (mes actual vs. anterior vs. mismo mes año anterior).
- Endpoints FastAPI + frontend Recharts (barras por día), drill-down mes→día, todo en kWh.
- Cartel de latencia ("datos disponibles hasta [fecha]") — Principio 4.

**DoD:** un usuario logueado ve su consumo diario real con comparación histórica y latencia explícita.

## Sprint 3 — Proyección + Home (M1) — *CU-H01, H03, H05, H06, H07*

**Meta:** dashboard de vistazo.

- Caso de uso **proyección mensual** con cascada de fallback (interanual → estacional → reciente → datos insuficientes) + banda de confianza; cache en `proyeccion_mensual`.
- `VecinosRepository` SQLite (bounding box + Haversine) → *Comparación con tu zona*.
- Home: bloques en orden confirmado (Consumo del mes → Comparación con tu zona → Proyección rango → Accesos directos → Timestamp).

**DoD:** Home muestra los 4 bloques Must; proyección siempre como **rango** con leyenda "se ajusta a medida que avanza el mes" (Principio 2).

## Sprint 4 — Objetivos de consumo (M6) — *CU-O01..O06*

**Meta:** fijar y seguir el objetivo mensual.

- `objetivo_sugerido` reutilizando `VecinosRepository` (promedio vecinos 150 m, mismo mes año anterior).
- Seteo en primer login (aceptar sugerido / ingresar manual), edición desde config (`ObjetivoConsumoRepository`).
- Indicadores 1 (vs. zona), 2 (días objetivo consumidos, texto dinámico ±5%, caso objetivo agotado), 3 (diario real vs. objetivo).

**DoD:** flujo completo de objetivo con los 3 indicadores y textos dinámicos. *Resolver antes los casos borde del punto abierto #3 (zona nueva sin datos, mínimo de vecinos por privacidad, no residenciales).*

## Sprint 5 — Mi Factura + Notificaciones (M3 + M4) — *CU-F01..F05, A01, A04*

**Meta:** cerrar la comunicación proactiva y el acceso a la factura.

- M3: explicación conceptual de ítems (sin montos), construcción del link de redirección a EPEC con los 2 inputs (Nº cliente / Nº contrato), ≤3 taps.
- `NotificationSender` → `PywebpushSender` + `SmtpEmailSender`; evaluación de alertas en el ETL (vencimiento próximo, factura disponible).
- M4: push configurable por tipo + configuración granular (`notificaciones_config`).

**DoD:** push de los 3 tipos llega y es configurable; botón de factura redirige correctamente con datos de prueba. *El endpoint de EPEC queda con investigación pendiente (punto abierto #1) — no bloquea: se avanza con inputs manuales.*

## Sprint 6 — Hardening, NFR y Should

**Meta:** calidad de release.

- **Should** diferidos: detección de consumo anómalo (z-score sobre `c(d)`) + alerta push, export CSV, email complementario, rate-limit de notificaciones.
- **NFR:** carga <3 s en 3G, caché PWA offline, responsive en todos los tamaños.
- **Privacidad:** disociación matemática de vecinos, mínimo de vecinos para no inferir individuos (Ley 25.326 / CU-NF02), opt-in analítica off por defecto.
- Observabilidad (structlog + Sentry/OTel), endurecimiento de seguridad y UAT.

**DoD:** NFR verificados, security-review + code-review aprobados antes de merge a `main`.

---

## Riesgos / puntos abiertos a destrabar en paralelo

1. **Acceso a Oracle** (credenciales read-only / VPN / réplica) — bloquea S1 con datos reales. Mitigado con *fake* + semilla.
2. **Auth de clientes** — ¿EPEC tiene identity provider (SSO) o auth propia? Define el adapter de `AuthProvider` (afecta S0).
3. **Endpoint de redirección EPEC** y obtención dinámica de Nº cliente/contrato — no bloqueante (S5 con inputs manuales).
4. **Objetivo sugerido, casos borde** — necesario antes de S4.
5. **Entorno dev** — proxy TLS bloqueando npm (`CONTEXT.md`) y `VAULT_PATH` sin completar — resolver en S0.
