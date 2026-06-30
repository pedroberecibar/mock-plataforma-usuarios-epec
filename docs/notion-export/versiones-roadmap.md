# Plataforma de Clientes EPEC — Versiones de la plataforma (Roadmap v2+)

> **Última actualización:** 2026-06-30 · Documento de producto.
> Recoge todo lo **removido del MVP** o etiquetado **"Definir en siguiente etapa"**, con su justificación.
> Regla del proyecto: ninguna remoción se borra sin rastro; queda acá como capacidad futura.

---

## 1. Funcionalidades removidas del MVP

Cada ítem se sacó del MVP por una razón explícita y queda contemplado para una versión futura.

| Funcionalidad | Por qué quedó fuera del MVP | Nota |
|---|---|---|
| **Valores monetarios en consumo** (montos en Home/Consumo/Objetivos, toggle pesos↔kWh) | Evitar discrepancias con la factura emitida que deriven en reclamos. La unidad del MVP es kWh. | *Contemplado para versión futura.* (Excepción ya implementada: Mi Factura sí muestra importes reales tomados de la fuente oficial de EPEC.) |
| **Bandas horarias / tarifa por tiempo de uso (TOU)** | El MVP asume tarifa plana; introducir Pico/Valle/Resto agrega complejidad de modelo y de UI no priorizada. | *Definir en siguiente etapa.* Condición de activación a evaluar en v2. |
| **Bloque subsidiario** | Fuera de alcance funcional del MVP. | *Contemplado para versión futura.* Crítico para el estudio conductual (ver §3). |
| **Cortes y Reclamos** | Módulo operativo no priorizado para el primer release de valor. | *Contemplado para versión futura.* |
| **Historial de factura in-app** | El MVP redirige al portal de EPEC en lugar de mantener historial propio. | *Definir en siguiente etapa.* |
| **App nativa (iOS/Android)** | El MVP es web responsive; no se construye app nativa. | *Contemplado para versión futura.* |

---

## 2. Mejoras técnicas / de granularidad para próximas etapas

| Tema | Estado | Próxima etapa |
|---|---|---|
| **Resolución cada 15 min** | El MVP llegó a granularidad horaria (perfiles) para medidores que lo soportan. | Filtro fino por día con consumo cada 15 min, donde el medidor lo permita. |
| **Cobertura de perfiles según medidor** | CLOU expone perfiles; otros medidores (p. ej. NANSEN) sin perfiles accesibles → se mantiene diario. | Ampliar fuentes/medidores con capacidad de perfiles. |
| **Deep-link de pago precargado** | Hoy redirige al portal y el usuario tipea Nº cliente/contrato (deep-link no precarga; iframe bloqueado). | Integración que precargue identificadores o pago embebido autorizado por EPEC. |
| **Push web end-to-end** | Infraestructura de envío presente; activación a validar. | Completar y validar push en producción. |
| **Rate-limit de notificaciones** | Diferido. | Ventana anti-duplicados sin bloquear alertas críticas. |
| **NFR de performance y PWA offline** | Diferido a hardening. | Carga <3s en 3G, service worker con caché de la serie, modo "datos sin conexión". |
| **Privacidad formal de vecinos** | Umbral mínimo a formalizar. | k-anonymity mínima antes de publicar comparaciones/sugeridos. |

---

## 3. Capacidad futura clave para el estudio conductual: Subsidios / RASE

> El estudio de economía conductual (UBP–EPEC) busca, además de la adopción de factura digital, **garantizar la inscripción al RASE de usuarios N2 (vulnerables) y N3 (ingresos medios)** ante reajustes tarifarios. Esto **no está en el MVP** y debe diseñarse.

### 3.1 Capacidades a definir

- **Segmentación N1/N2/N3** del cliente y exposición (o uso interno) de su categoría de subsidio.
- **Estado de inscripción al RASE** del cliente y orientación hacia la inscripción/renovación.
- **Nudges de inscripción**: mensajes persuasivos, recordatorios y disparadores en momentos de alta atención (vencimiento, aumento tarifario).
- **Medición de impacto**: instrumentación para el piloto controlado del estudio (grupos, variantes de mensaje, métricas de conversión).

### 3.2 Insumos ya disponibles en el MVP

- **Mi Cuenta** ya trae la **tarifa legible** del cliente desde Oracle (`/cuenta` → `tarifa`): base para segmentar audiencias una vez definidas las reglas de subsidio.
- **M4 Alertas** (config granular + envío email/push) ofrece el canal para entregar nudges.
- **M3 Mi Factura** es el contexto natural donde el aumento tarifario se vuelve saliente para el usuario.

### 3.3 Dependencias externas

- Reglas oficiales de categorización N1/N2/N3 y del registro RASE.
- Fuente de datos del estado de subsidio/inscripción del cliente (a definir con EPEC).
- Marco legal/privacidad para tratar la categoría socioeconómica del usuario.

---

## 4. Relación con el MVP

Para el detalle de lo que ya está implementado y los casos de uso cubiertos, ver la página **[MVP — Estado actual y casos de uso]**.
