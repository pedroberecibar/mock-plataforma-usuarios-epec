# Plataforma de Clientes EPEC — MVP: Estado actual y casos de uso

> **Última actualización:** 2026-06-30 · **Estado del repositorio:** rama de trabajo `spike/oracle-perfiles-georef` sobre `main`.
> Documento de producto/funcionalidad/arquitectura. No incluye herramientas internas de desarrollo.
> Reconciliado **contra el código fuente** (routers FastAPI y casos de uso de la capa `application`), no contra el plan original.

---

## 1. Propósito del MVP

Aplicación **web responsive** (sin app nativa) para que un cliente de EPEC entienda y gestione su consumo eléctrico. El MVP se concentra en:

- Mostrar el **consumo eléctrico** del cliente con datos reales, en **kWh**.
- Compararlo en el tiempo (mes a mes, año a año) y contra **vecinos de su zona**.
- Proyectar el consumo al cierre del mes.
- Fijar y seguir un **objetivo de consumo**.
- Acercar la **factura** (importe, vencimiento, acceso al pago) y **alertas proactivas**.
- Exponer los **datos de la cuenta** del cliente (identidad, suministro, tarifa, medidor).

Fuente única de verdad: **Oracle `PRODEBS_SEE`** (interno, solo lectura), cacheado en una base local. Cero datos sintéticos: si falta un dato, se devuelve `null`/vacío, nunca se inventa.

---

## 2. Reglas de producto

### 2.1 Reglas absolutas (vigentes)

- **Unidad única: kWh.** Escrito exactamente "kWh".
- **Tarifa plana:** sin bandas horarias (Pico / Valle / Resto / TOU).
- **Sin valores monetarios en los módulos de consumo.** Se evita mostrar montos en Home/Consumo/Objetivos para prevenir discrepancias con la factura emitida que generen reclamos.
- **Removidos del MVP:** bloque subsidiario, Cortes y Reclamos, toggle pesos/kWh.
- **Toda remoción deja nota** "Contemplado para versión futura" (no se borra sin rastro). Ver página [Versiones de la plataforma (Roadmap v2+)].
- **Terminología fija:** "objetivo de consumo", "consumo acumulado del mes", "ritmo diario objetivo", "proyección al cierre", "vecinos".
- **Privacidad:** las comparaciones zonales se publican solo como agregados; nunca se expone el consumo individual de un tercero (Ley 25.326).

### 2.2 Reglas que evolucionaron durante el desarrollo

Estas decisiones se tomaron sobre la marcha y **modifican lo definido originalmente**. Se documentan explícitamente:

| Regla original | Estado actual | Motivo |
|---|---|---|
| "Mi Factura sin montos, solo explicación conceptual" | **Mi Factura muestra importe real, vencimiento, deuda total y PDF** vía API oficial de EPEC. | Se halló el endpoint `POST /api/documentos/a-pagar` (apiKey pública `web-prod`) que devuelve datos reales de pago; se incorporó como módulo de valor. La regla de "sin montos" se mantiene en Home/Consumo/Objetivos. |
| "Granularidad máxima = consumo diario; sin resolución horaria" | **Se agregó perfil de consumo horario y hora pico** (ADR-003) para medidores telemedibles con capacidad de perfiles. | Algunos medidores (CLOU) exponen perfiles cada 15 min en Oracle; se habilitó la granularidad horaria donde el medidor lo soporta. Para medidores sin perfiles, se mantiene diario. |
| "5 módulos (M1, M2, M3, M4, M6)" | **Se agregó el módulo Mi Cuenta (M5)**. | El endpoint Oracle `VM_INTELIGENTES` permite exponer identidad, dirección, tarifa legible y medidor. |
| "Vecinos = radio de 150 m (bounding box + Haversine)" | **Vecinos = misma subestación eléctrica** (`GEOREF.VW_INTELIGENTES`). | El criterio geográfico por radio resultó menos representativo que el agrupamiento por subestación. |

---

## 3. Módulos y alcance funcional

| Módulo | Estado | Núcleo |
|---|---|---|
| **M1 — Home** | ✅ Implementado | Consumo del mes (vs mes anterior y vs año anterior), comparación con tu zona, proyección al cierre (rango), accesos directos, timestamp de frescura. |
| **M2 — Consumo** | ✅ Implementado | Serie diaria en kWh, comparación histórica, drill-down mes→día, detección de consumo anómalo, perfil horario + hora pico, export CSV, cartel de latencia. |
| **M3 — Mi Factura** | ✅ Implementado | Importe, vencimiento, deuda y PDF reales; acceso al pago online; link de redirección al portal EPEC con Nº cliente / Nº contrato. |
| **M4 — Alertas** | ✅ Implementado (núcleo) | Config granular por tipo; evaluación de objetivo superado y vencimiento próximo con envío de email. |
| **M5 — Mi Cuenta** | ⚠️ Backend listo, UI pendiente | Datos personales (con PII enmascarada), suministro, tarifa, medidor. |
| **M6 — Objetivos** | ✅ Implementado | Objetivo sugerido (promedio de vecinos, mismo mes año anterior), seteo/edición, 3 indicadores con textos dinámicos, barra de progreso. |
| **Ingesta / pipeline** | ✅ Implementado | Carga e idempotencia de la serie desde Oracle; poblado on-demand y refresco síncrono. |
| **Autenticación** | ✅ Implementado | Login por Nº de suministro + password (argon2id), token, perfil `/me`. |

---

## 4. Listado de casos de uso (reconciliado con el código)

Leyenda: ✅ implementado · ⚠️ parcial · ❌ pendiente/diferido. La columna **Evidencia** referencia el endpoint o caso de uso real.

### M1 — Home

| CU | Descripción | Estado | Evidencia |
|---|---|---|---|
| CU-H01 | Consumo del mes en kWh | ✅ | `GET /home` → `consumo_mes.total_kwh` |
| CU-H02 | Variación vs mes anterior | ✅ | `GET /home` → `vs_mes_anterior_pct` |
| CU-H03 | Variación vs mismo mes año anterior | ✅ | `GET /home` → `vs_anio_anterior_pct` |
| CU-H04 | Comparación con tu zona (vecinos) | ✅ | `GET /home` → `comparacion_zona` (`promedio_vecinos_kwh`, `n_vecinos`, `diferencia_pct`) |
| CU-H05 | Proyección al cierre como rango + bandera de confianza | ✅ | `GET /home` → `proyeccion` (`rango_inferior_kwh`, `rango_superior_kwh`, `metodo_aplicado`, `bandera_confianza`) |
| CU-H06 | Accesos directos a factura | ✅ | UI Home (enlaza a M3) |
| CU-H07 | Timestamp / latencia de datos | ✅ | `GET /home` → `datos_hasta`, `timestamp` |

### M2 — Consumo

| CU | Descripción | Estado | Evidencia |
|---|---|---|---|
| CU-C01 | Serie de consumo diario (barras por día) en kWh | ✅ | `GET /consumo/diario` |
| CU-C02 | Drill-down mes→día (detalle del día) | ✅ | `GET /consumo/dia` (kWh del día, mismo día año anterior, promedio zona) |
| CU-C03 | Comparación histórica (mes actual / anterior / año anterior) | ✅ | `GET /consumo/comparacion` |
| CU-C04 | Comparación con la zona en la vista de consumo | ✅ | `GET /consumo/comparacion` → `zona_mes_actual` |
| CU-C05 | Transparencia de latencia ("datos disponibles hasta…") | ✅ | `datos_hasta` en respuestas de consumo |
| CU-C06 | Detección de consumo anómalo (z-score) | ✅ | `GET /consumo/anomalia` (era *Should*; ya implementado) |
| CU-C07 | Exportación CSV de la serie | ✅ | `GET /consumo/export/csv` (era *Should*; ya implementado) |
| CU-C08 | Perfil de consumo horario + hora pico | ✅ | `GET /consumo/horario`, `GET /consumo/hora-pico` (extensión ADR-003, según capacidad del medidor) |

### M3 — Mi Factura

| CU | Descripción | Estado | Evidencia |
|---|---|---|---|
| CU-F01 | Datos de factura (importe, vencimiento, deuda, estado, PDF) | ✅ | `GET /factura/datos` |
| CU-F02 | Documentos a pagar (período, Nº factura, importe, vencimiento) | ✅ | `GET /factura/documentos` |
| CU-F03 | Acceso al pago online | ✅ | `pago_online` + `url_pdf` en `/factura/datos` |
| CU-F04 | Redirección al portal EPEC con Nº cliente / Nº contrato (≤3 taps) | ✅ | `GET /factura/link` (inputs manuales; deep-link no precarga, ver Punto abierto) |
| CU-F05 | Alerta de vencimiento próximo | ✅ | `POST /alertas/evaluar-vencimiento` |

### M4 — Alertas

| CU | Descripción | Estado | Evidencia |
|---|---|---|---|
| CU-A01 | Configuración granular por tipo de alerta | ✅ | `GET/PATCH /alertas/config` |
| CU-A02 | Alerta de objetivo de consumo superado | ✅ | `POST /alertas/evaluar-objetivo` |
| CU-A03 | Alerta de vencimiento de factura | ✅ | `POST /alertas/evaluar-vencimiento` |
| CU-A04 | Email complementario de alertas | ✅ | envío por `NotificationSender` (email) en los casos de uso de evaluación |
| CU-A05 | Notificaciones push web | ⚠️ | infraestructura de envío presente; activación push end-to-end a confirmar |
| CU-A06 | Rate-limit de notificaciones | ❌ | diferido a hardening |

### M5 — Mi Cuenta

| CU | Descripción | Estado | Evidencia |
|---|---|---|---|
| CU-CT01 | Datos personales con PII enmascarada (DNI/CUIT) | ⚠️ backend | `GET /cuenta` → `personales` (DNI cifrado en cache, enmascarado en respuesta) |
| CU-CT02 | Datos del suministro (dirección, barrio, localidad, estado) | ⚠️ backend | `GET /cuenta` → `suministro` |
| CU-CT03 | Tarifa legible (código, descripción, grupo, clase, tensión) | ⚠️ backend | `GET /cuenta` → `tarifa` |
| CU-CT04 | Medidor (número, marca, fase, inteligente desde) | ⚠️ backend | `GET /cuenta` → `medidor` |
| CU-CT05 | Pantalla UI de Mi Cuenta | ❌ | diseño de UI pendiente (endpoint listo) |

### M6 — Objetivos de consumo

| CU | Descripción | Estado | Evidencia |
|---|---|---|---|
| CU-O01 | Objetivo sugerido (promedio vecinos, mismo mes año anterior) | ✅ | `GET /objetivos/sugerido` |
| CU-O02 | Seteo del objetivo (primer login / manual) | ✅ | `POST /objetivos` |
| CU-O03 | Lectura del objetivo vigente | ✅ | `GET /objetivos` |
| CU-O04 | Edición del objetivo | ✅ | `POST /objetivos` (modal de edición desde el hero) |
| CU-O05 | Indicadores 1/2/3 (vs zona, ritmo/días, diario real vs objetivo) | ✅ | `GET /objetivos/estado` (incluye `texto_dinamico`, `excedente_kwh`, etc.) |
| CU-O06 | Barra de progreso + alerta de objetivo superado | ✅ | UI Objetivos + `POST /alertas/evaluar-objetivo` |

### Transversales (autenticación, ingesta, NFR)

| CU | Descripción | Estado | Evidencia |
|---|---|---|---|
| CU-AU01 | Login por Nº de suministro + password | ✅ | `POST /auth/login` (hash argon2id) |
| CU-AU02 | Perfil del usuario autenticado | ✅ | `GET /auth/me` |
| CU-IN01 | Ingesta de consumo por rango de fechas | ✅ | `POST /ingest/consumo` |
| CU-IN02 | Poblado on-demand del suministro (background) | ✅ | `POST /ingest/poblar` |
| CU-IN03 | Refresco síncrono ("Actualizar") | ✅ | `POST /ingest/refrescar` |
| CU-NF01 | Cero dato sintético; faltante → vacío/`null`/503 | ✅ | política transversal (ADR-002) |
| CU-NF02 | Privacidad de vecinos (mínimo de agregación) | ⚠️ | umbral k-anonymity a formalizar en hardening |
| CU-NF03 | Performance <3s en 3G, caché PWA offline | ❌ | diferido a hardening |

---

## 5. Arquitectura técnica (estado actual)

- **Patrón:** Arquitectura hexagonal (Ports & Adapters) en 4 capas — `domain` · `application` · `infrastructure` · `interface`. La capa `domain` no importa infraestructura; ningún caso de uso depende de una librería concreta (Oracle, SQLite, JWT, push/email) — siempre vía su puerto. Validado por test de arquitectura (ADR-001).
- **Backend:** Python 3.12 + FastAPI. Routers: `auth`, `home`, `consumo`, `factura`, `alertas`, `objetivos`, `cuenta`, `ingest`.
- **Frontend:** React + TypeScript (Vite), web responsive.
- **Datos:** Oracle `PRODEBS_SEE` (solo lectura) como origen; base local como **cache ingestada**. La serie de consumo diario `c(d)` es la base de Home, Consumo, anomalías, proyección y objetivos.
- **Puertos del proyecto:** `ConsumoDiarioRepository`, `ConsumoHorarioRepository`, `ObjetivoConsumoRepository`, `VecinosRepository`, `MedicionSourceReader`, `ProyeccionRepository`, `FacturaSourceReader`, `FacturaVerificacionPort`, `CuentaReader`, `UsuarioRepository`, `SuministroRepository`, `NotificacionConfigRepository`, `NotificationSender`, `AuthProvider`, `PiiCipher`, `CuentaSensibleRepository`.
- **Composition root:** el cableado real↔fake se resuelve en un único punto; con Oracle disponible usa adapters reales, si no, fakes con dataset semilla.
- **Seguridad:** passwords argon2id; PII (DNI/CUIT) cifrada en cache y enmascarada en la respuesta; queries parametrizadas.
- **ADRs vigentes:** ADR-001 (SQLite + Ports & Adapters), ADR-002 (entornos y datos: real Oracle sin sintético), ADR-003 (telemedible + capacidad de perfiles horarios).

---

## 6. Estado del proyecto

- **Cobertura de tests (última verificación documentada):** backend ~407 tests · frontend ~161 tests · linters/type-check limpios; cadena de migraciones lineal que aplica sobre base fresca.
- **Terminado:** Home, Consumo (incl. anomalía, horario, CSV, drill-down), Objetivos (3 indicadores + progreso), Mi Factura (datos reales + link), Alertas (config + evaluación objetivo/vencimiento por email), autenticación, ingesta/refresco.
- **Parcial:** Mi Cuenta (backend listo, falta UI); push web end-to-end; privacidad formal de vecinos.
- **Pendiente / hardening:** rate-limit de notificaciones, NFR de performance y caché PWA offline, UAT.

---

## 7. Puntos de contacto para intervención conductual

> Sección orientada al estudio de economía conductual (nudges) sobre **adopción de factura digital** y **subsidios**. Identifica dónde la app ya puede alojar intervenciones sin tocar las reglas duras del MVP.

### 7.1 Factura digital — cubierto (palanca disponible hoy)

- **M3 Mi Factura** ya centraliza importe, vencimiento, PDF y acceso al pago online: es el punto natural para nudges de adopción digital (p. ej. destacar el PDF/pago online como vía preferente).
- **M4 Alertas** (vencimiento próximo, factura disponible) son disparadores proactivos ideales para mensajes persuasivos por email/push, con configuración granular ya existente.
- **M1 Home** tiene accesos directos a factura: ubicación de alta visibilidad para un nudge de "pasate a factura digital".

### 7.2 Subsidio / RASE (N2/N3) — **brecha respecto al estudio**

- El **bloque subsidiario está explícitamente fuera del MVP** (regla absoluta vigente). Hoy la app **no** muestra el segmento tarifario del cliente orientado a subsidios ni gestiona la inscripción al RASE.
- Para que el estudio pueda intervenir sobre la inscripción al RASE de usuarios N2/N3, esta capacidad debe **diseñarse e incorporarse**. Su definición se traslada a la página [Versiones de la plataforma (Roadmap v2+)].
- **Insumo disponible:** el módulo Mi Cuenta ya expone la tarifa legible del cliente desde Oracle (`/cuenta` → `tarifa`), lo que puede servir de base para segmentar audiencias del estudio una vez definidas las reglas de subsidio.

---

## 8. Puntos abiertos (vigentes)

1. **Deep-link de pago EPEC** no precarga Nº contrato/cliente (probado); el botón redirige al portal y el usuario tipea. Iframe inviable (`X-Frame-Options: DENY`).
2. **Push web end-to-end** a validar en producción.
3. **Umbral de privacidad de vecinos** (k-anonymity mínima) a formalizar antes de publicar comparaciones/sugeridos.
4. **UI de Mi Cuenta** a diseñar (backend listo).
5. **Subsidio/RASE**: fuera de alcance del MVP; requerido por el estudio conductual → ver Roadmap v2+.
