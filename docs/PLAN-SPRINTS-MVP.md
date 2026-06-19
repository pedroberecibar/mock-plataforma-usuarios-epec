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

## Sprint 7 — Barra de progreso, alerta OBJETIVO_SUPERADO y seed (completado 2026-06-18)

**Meta:** instrumentar el seguimiento visual del objetivo y habilitar contraseñas en producción.

- `EvaluarObjetivoConsumoUseCase`: compara consumo acumulado vs objetivo (threshold 80%), despacha `TipoAlerta.OBJETIVO_SUPERADO` por email.
- `POST /alertas/evaluar-objetivo` en `alertas_router.py`; `get_email` en `UsuarioRepository`.
- `ObjetivosPage`: barra `role="progressbar"` con color verde/warning/error (threshold 80%), alerta "superado" cuando `≥ 100%`.
- `scripts/seed_passwords.py`: hashea con argon2id, nunca acepta passwords por CLI args, soporta `--db URL`.

**DoD:** 222 tests backend + 52 frontend · mypy ok · ruff ok · tsc ok.

---

## Sprint 8 — Completar Objetivos de consumo (M6) — *CU-O01..O06 restantes*

**Meta:** cerrar el único módulo Must con indicadores aún sin implementar.

**Dependencia previa:** los casos borde del objetivo sugerido (punto abierto #3 y #4 del plan) deben estar resueltos antes de arrancar: mínimo de vecinos para respetar privacidad (Ley 25.326), tratamiento de suministros no residenciales en el radio, fallback cuando no hay datos del mismo mes año anterior.

### Backend

- `CalcularObjetivoSugeridoUseCase`: reutiliza `VecinosRepository.get_vecinos(radio=150)` + `ConsumoDiarioRepository` para obtener el promedio del mismo mes del año anterior entre los vecinos del radio. Puerto → Fake → SQLite adapter → test cada capa.
- `GET /objetivos/sugerido/{suministro_id}?mes=YYYY-MM` → `{ valor_kwh, n_vecinos, sin_datos }`.
- `GET /objetivos/{suministro_id}/estado?mes=YYYY-MM` → nuevo endpoint que calcula y devuelve los 3 indicadores:
  - Indicador 1: `objetivo_kwh`, `promedio_vecinos_kwh`, `n_vecinos`, `diferencia_pct`.
  - Indicador 2: `dias_transcurridos`, `dias_objetivo_consumidos`, `texto_dinamico` (enum: `bajo_ritmo | en_ritmo | sobre_ritmo | agotado`), `excedente_kwh` (solo si `agotado`).
  - Indicador 3: `consumo_diario_real_kwh` (dato del día más reciente), `consumo_diario_objetivo_kwh` (objetivo / días del mes).

### Frontend

- **Onboarding primer login**: si `GET /objetivos` devuelve 404, redirigir a pantalla de bienvenida que muestra el objetivo sugerido con CTA "Aceptar sugerido" / "Ingresar mi objetivo". Guardar y navegar al Home.
- **Indicador 1** en `ObjetivosPage`: chip comparativo objetivo vs promedio zonal (barra o porcentaje de diferencia).
- **Indicador 2** en `ObjetivosPage`: texto dinámico según `texto_dinamico`, barra de días consumidos vs días transcurridos, palanca accionable cuando `sobre_ritmo` o `agotado`, excedente en kWh cuando `agotado`.
- **Indicador 3** en `ObjetivosPage`: comparador (chip o barra mini) `consumo_diario_real_kwh` vs `consumo_diario_objetivo_kwh`.
- Integrar trigger `POST /alertas/evaluar-objetivo` automáticamente al cargar `ObjetivosPage` (o desde `HomePage` al mount).

**DoD:** flujo completo de primer login con sugerido; 3 indicadores renderizados con textos dinámicos y palancas; tests backend verdes por capa; tests frontend para cada indicador y caso borde de Indicador 2 (bajo_ritmo / en_ritmo / sobre_ritmo / agotado).

---

## Sprint 9 — Drill-down Consumo (M2) + Alerta de vencimiento (M3/M4) — *CU-C02, CU-F05*

**Meta:** cerrar los últimos Must de M2 y M3.

**Dependencia previa (alerta vencimiento):** decidir cómo llega la fecha de vencimiento de la factura al sistema (campo `fecha_vencimiento` en tabla `suministros`, o input manual del usuario, o derivación de ciclo de facturación). Resolver antes de arrancar la historia de vencimiento.

### Drill-down Consumo (CU-C02)

- Backend: `GET /consumo/{suministro_id}/dia/{fecha}` → consumo puntual del día + promedio diario personal del mes (para contexto).
- Frontend `ConsumoPage`: al hacer click/tap en una barra de `GraficoConsumoDiario`, mostrar panel lateral o modal con consumo del día en kWh y comparación "X% respecto a tu promedio diario". Botón de retroceso vuelve a la vista mensual conservando el mes.

### Alerta de vencimiento próximo (CU-F05)

- Backend: `TipoAlerta.VENCIMIENTO_PROXIMO` en `evaluar_alertas.py` + asunto y cuerpo del email; se dispara cuando `hoy >= fecha_vencimiento - N días` (N configurable, default 3).
- Endpoint `POST /alertas/evaluar-vencimiento` (o agregar al job de ingesta existente): evalúa todos los suministros con `fecha_vencimiento` configurada.
- Frontend `AlertasPage`: mostrar alerta de tipo `vencimiento_proximo` con acceso directo al flujo de factura (≤ 3 taps al sitio de EPEC — CU-F04).

**DoD:** click en barra diaria abre detalle del día; email de vencimiento se despacha correctamente en tests; `AlertasPage` renderiza el tipo vencimiento con acceso a factura.

---

## Sprint 10 — Hardening, NFR y Should *(equivale al S6 del plan original, extendido)*

**Meta:** calidad de release — performance, privacidad, observabilidad y features Should diferidos.

### Should diferidos (M2, M4)

- **Consumo anómalo** (CU-C06): z-score sobre la serie `c(d)` del usuario; si un día supera el umbral, mostrar alerta en `ConsumoPage` ("El jueves tu consumo fue 40% mayor a tu promedio diario") con palanca accionable. El promedio de referencia es la misma serie `c(d)` de la Especificación técnica de proyección.
- **Exportación CSV** (CU-C07): botón en `ConsumoPage` (solo en viewport web) que descarga un CSV con la serie diaria del rango seleccionado.
- **Rate-limit de notificaciones** (CU-A06): agregar columna `ultimo_envio_por_tipo` en `notificaciones_config`; suprimir duplicados dentro de la ventana configurada sin bloquear alertas críticas.
- **Email complementario** (CU-A05): asegurar que todos los tipos de alerta (vencimiento, consumo anómalo, objetivo superado) disparan email si el canal está habilitado.

### NFR

- Performance: medir y ajustar hasta carga inicial < 3 s en 3G simulado (Lighthouse CI).
- Caché PWA: service worker con caché de la serie de consumo para uso offline básico; indicar "Datos sin conexión" cuando la caché está activa.
- Responsive: smoke test visual en viewports 375px, 768px, 1280px.

### Privacidad (CU-NF02)

- Definir y aplicar el mínimo de vecinos antes de publicar comparación o sugerido (umbral k-anonymity mínima a acordar; si `n_vecinos < k`, devolver `sin_datos`).
- Revisar que ningún endpoint filtre consumos individuales de terceros.
- Opt-in analítica avanzada off por defecto.

### Producción

- Alembic: `alembic upgrade head` sobre la DB de producción + smoke test end-to-end con datos reales.
- Observabilidad: structlog + Sentry/OTel básico.
- Endurecimiento de seguridad: security-review (agente `security-reviewer`) + code-review (agente `code-reviewer`) obligatorios antes del merge final a `main`.
- UAT con usuarios internos.

**DoD:** NFR verificados por Lighthouse CI; security-review y code-review aprobados; zero Must pendientes; migración de producción ejecutada sin errores.

---

## Riesgos / puntos abiertos a destrabar en paralelo

1. **Acceso a Oracle** (credenciales read-only / VPN / réplica) — bloquea S1 con datos reales. Mitigado con *fake* + semilla.
2. **Auth de clientes** — ¿EPEC tiene identity provider (SSO) o auth propia? Define el adapter de `AuthProvider` (afecta S0).
3. **Endpoint de redirección EPEC** y obtención dinámica de Nº cliente/contrato — no bloqueante (S5 con inputs manuales).
4. **Objetivo sugerido, casos borde** — necesario antes de S4.
5. **Entorno dev** — proxy TLS bloqueando npm (`CONTEXT.md`) y `VAULT_PATH` sin completar — resolver en S0.
