# Prompts para Google Stitch — Plataforma Clientes EPEC (MVP)

> **Fuentes:** documento de producto "Plataforma clientes EPEC" (Notion, revisión junio 2026) + `docs/EPEC Design System/` (`README.md`, `colors_and_type.css`).
> **Alcance:** solo MVP — Home, Consumo, Mi Factura, Alertas/Notificaciones, Objetivos de consumo, más login, onboarding y configuración. Los módulos v2/v3 (Ahorro, Asistente GenAI, Prosumidor) quedan fuera.

---

## 1. Cómo usar este documento

1. Crear un proyecto en Google Stitch en modo **Mobile** (el viewport móvil es la referencia de diseño de la plataforma). Para las pantallas marcadas como **Desktop**, usar un proyecto en modo **Web**.
2. Para cada pantalla, pegar en Stitch: el bloque **Global Design Context** (sección 2) **+ el prompt de la pantalla** (sección 4). Cada prompt es autocontenido.
3. Generar **una pantalla por prompt**, en el orden listado. Stitch funciona mejor por pantalla que con descripciones de toda la app, y mejor con refinamientos incrementales ("make the projection card more prominent") que con prompts re-escritos desde cero.
4. Antes de generar, configurar el **theme** del proyecto con los tokens del Apéndice A (color primario, tipografía, radios) para que todas las pantallas salgan consistentes.
5. Verificar cada resultado contra la **checklist de reglas de producto** (sección 5). Si Stitch muestra precios, símbolos `$`, datos por hora o secciones de cortes/reclamos, corregir con un refinamiento: *"Remove any monetary values; the only unit in this product is kWh."*

**Datos de ejemplo consistentes en todos los prompts** (usarlos tal cual para que las pantallas cuenten una misma historia): mes en curso **junio 2026, día 11 de 30** · consumo acumulado **78 kWh** · junio 2025 a esta altura **84 kWh** · mayo a esta altura **73 kWh** · promedio vecinos 150 m **86 kWh** · proyección al cierre **"198 – 226 kWh"** (mayo cerró en 205 kWh) · objetivo mensual **210 kWh** (sugerido 215 kWh) · datos disponibles hasta **10/06/2026, 23:59**.

---

## 2. Global Design Context (pegar antes de cada prompt)

```text
GLOBAL DESIGN CONTEXT — EPEC Customer Platform

Product: responsive web app for residential electricity customers of EPEC, the state-owned
power utility of Córdoba, Argentina. Mobile viewport is the primary design reference.
Its purpose: help users understand, track and optimize their electricity consumption,
always expressed in kWh.

Brand & visual style:
- Primary brand color: deep forest green #124e2f. Use it for the top app bar, primary
  buttons, active nav states and key accents. Light green tints #edf5f0 / #d4eedd for
  highlighted cards, selected states and positive backgrounds.
- Neutrals: page background #f5f7f6, surfaces white #ffffff, light gray 1px borders
  (#d5ddd9), primary text #111614, secondary text #4a5550.
- Semantic colors: success #1d8348 (light #d4edda), warning #e6910a (light #fff3cd),
  error #c0392b (light #fde8e8), info #1565c0 (light #dbeafe).
- Typography: Roboto for headings, body and labels. Space Grotesk for technical figures
  (kWh numbers, meter data, dates) to give data a distinct, precise look.
- Institutional, clean, data-forward aesthetic: white cards with subtle 1px borders,
  very light shadows, border radius 4–8px, 4px spacing grid. No gradients, no decorative
  photography, no illustrations, no emoji. Icons: Lucide-style thin line icons.
- Tone of copy: formal Argentine Spanish ("usted" register), sentence case, declarative,
  no exclamation marks. ALL UI text must be in Spanish exactly as written in the prompt.

Non-negotiable product rules (apply to every screen):
1. kWh is the ONLY unit. Never show money, prices, $ or pesos anywhere.
2. Consumption projections are always shown as a RANGE (e.g. "198 – 226 kWh"), never a
   single exact number, always with the caption "Se ajusta a medida que avanza el mes".
3. Bad news always comes with an actionable tip, phrased as an opportunity, never as
   punishment.
4. Data latency is always declared explicitly (e.g. "Datos disponibles hasta el
   10/06/2026, 23:59"). Never pretend data is real-time.
5. Maximum data granularity is DAILY consumption. No hourly charts, no time-of-use
   bands, no peak/valley indicators.
6. No outage status, no claims/complaints sections, no subsidy blocks.
```

---

## 3. Mapa de navegación

```text
                         ┌────────────────────────────┐
   Login ──► Onboarding ─► Home (Dashboard)           │
            (objetivo)   │  ├─ campana ► Notificaciones
                         │  └─ engranaje ► Configuración
                         │       ├─ Editar objetivo
                         │       └─ Config. de notificaciones
                         │
   Bottom nav (4 tabs): [ Inicio | Consumo | Objetivos | Factura ]
                            │
                            └─ Consumo ► Detalle de día (drill-down)
                               (en desktop: + export CSV / multi-período)
```

- **Bottom nav móvil (4 ítems):** Inicio (`house`), Consumo (`bar-chart-3`), Objetivos (`target`), Factura (`receipt`).
- **Top bar:** logo EPEC a la izquierda, campana de notificaciones (`bell`) y engranaje (`settings`) a la derecha.

---

## 4. Prompts por pantalla

### 4.1 · Login — *Mobile*

```text
SCREEN: Login

Design a mobile login screen for the EPEC customer platform.

Layout, top to bottom:
1. Top half: deep green #124e2f background area with the EPEC logo (white square logo
   with a stylized "E") centered, and below it the app name "EPEC Clientes" in white
   Roboto, with the subtitle "Su consumo eléctrico, claro y en kWh".
2. White card overlapping the green area, radius 8px, containing the form:
   - Text input, label "Correo electrónico", placeholder "nombre@correo.com"
   - Password input, label "Contraseña", with show/hide eye icon
   - Link aligned right: "¿Olvidó su contraseña?"
   - Full-width primary button, green #124e2f, white text: "Ingresar"
3. Below the card: secondary text "¿Primera vez en la plataforma?" with link
   "Crear cuenta".
4. Footer caption in muted gray: "EPEC — Empresa Provincial de Energía de Córdoba".

Institutional and sober: no illustrations, no social login buttons, generous spacing.
```

---

### 4.2 · Onboarding — Objetivo de consumo sugerido — *Mobile*

```text
SCREEN: Onboarding — set monthly consumption goal (first login)

Design a mobile onboarding screen shown on first login, where the user sets their
monthly electricity consumption goal in kWh.

Layout, top to bottom:
1. Top bar: small EPEC logo, step indicator "Paso 1 de 1".
2. Heading: "Defina su objetivo de consumo mensual".
3. Supporting paragraph: "Muchos clientes no conocen su consumo habitual. Le sugerimos
   un objetivo calculado a partir del consumo promedio de su zona."
4. Highlighted suggestion card (light green background #edf5f0, 1px green border):
   - Label: "Objetivo sugerido"
   - Big figure in Space Grotesk: "215 kWh"
   - Caption: "Promedio de consumo de sus vecinos en un radio de 150 m durante
     junio del año pasado."
5. Full-width primary green button: "Aceptar objetivo sugerido".
6. Divider with text "o".
7. Secondary option: outlined input field, label "Ingresar mi propio objetivo",
   numeric value with fixed suffix "kWh", plus an outlined secondary button
   "Guardar objetivo manual".
8. Footer caption: "Podrá editar su objetivo en cualquier momento desde Configuración."

Calm, instructional feel. The suggested-goal card is the visual protagonist.
```

---

### 4.3 · Home (Dashboard) — *Mobile*

```text
SCREEN: Home dashboard

Design the mobile home dashboard. Exact block order is mandatory.

Top bar: green #124e2f, EPEC logo left, bell icon and settings gear right.
Greeting under it: "Hola, Pedro" with subtitle "Junio 2026 · día 11 de 30".

Block 1 — Card "Consumo del mes" (the hero card):
- Big figure in Space Grotesk: "78 kWh" with label "Consumo acumulado del mes".
- Two comparison rows below it, each with a direction arrow chip:
  a) "En junio 2025 llevabas 84 kWh a esta altura" with a green downward arrow chip
     "↓ 7%" (positive, less consumption than last year).
  b) "En mayo llevabas 73 kWh a esta altura" with an amber upward arrow chip "↑ 7%"
     (warning, more than last month).

Block 2 — Card "Comparación con tu zona":
- Compact horizontal comparison: "Vos: 78 kWh" vs "Promedio de tu zona: 86 kWh"
  shown as two horizontal bars (user bar shorter, in green).
- Positive reinforcement line with a leaf or check icon: "Consumís 9% menos que el
  promedio de tus vecinos en un radio de 150 m. Buen trabajo."

Block 3 — Card "Proyección al cierre":
- Range figure in Space Grotesk: "198 – 226 kWh" (never a single number).
- Caption: "Se ajusta a medida que avanza el mes".
- Reference line: "Mayo cerró en 205 kWh".
- Small neutral confidence badge: "Confianza media".

Block 4 — "Accesos directos": two side-by-side action buttons, "Ver factura"
(receipt icon) and "Pagar factura" (external-link icon), both outlined green.

Block 5 — Footer caption in muted gray: "Última actualización: 11/06/2026, 06:15 ·
Datos disponibles hasta el 10/06/2026, 23:59".

Bottom navigation, 4 tabs with Lucide icons: "Inicio" (active, green), "Consumo",
"Objetivos", "Factura". No money values anywhere, only kWh.
```

---

### 4.4 · Home — estado cliente nuevo (sin histórico) — *Mobile*

```text
SCREEN: Home dashboard — empty state for a new customer

Same mobile home dashboard structure as the regular Home (top bar, greeting, bottom
nav with "Inicio" active), but for a brand-new customer with less than 30 days of
meter readings.

Block 1 — Card "Consumo del mes": shows the accumulated figure "12 kWh" normally, but
instead of comparison rows it shows one muted info line with an info icon:
"Aún no hay histórico comparable disponible. Las comparaciones aparecerán a partir
de tu segundo mes."

Block 2 — Card "Comparación con tu zona": normal content (zone average exists).

Block 3 — Card "Proyección al cierre" in empty state: instead of a range, an info
icon with the text "Aún no hay datos suficientes para proyectar tu consumo. Necesitamos
al menos 30 días de lecturas." Soft neutral background, no alarming colors.

Block 4 — "Accesos directos" and Block 5 — update timestamp: same as regular Home.

The empty states must look intentional and reassuring, not like errors: muted gray
text, light backgrounds, no red.
```

---

### 4.5 · Consumo — *Mobile*

```text
SCREEN: Consumption history (daily)

Design the mobile consumption analysis screen. Daily resolution is the maximum
granularity: no hourly data anywhere.

Top bar: green, title "Consumo", bell and settings icons.

1. Month selector row: chevron-left, "Junio 2026", chevron-right.
2. Summary row: total "78 kWh acumulados" plus a segmented comparison control with
   two pills: "vs. mayo" (selected) and "vs. junio 2025".
3. Main card — daily bar chart: one vertical green bar per day of June (days 1–10
   with data), Y axis labeled "kWh", X axis showing day numbers. Day 5 bar is
   highlighted in amber (anomaly). Days 11–30 shown as empty slots. One day (day 8)
   rendered differently from a zero-consumption day: a hatched/ghost bar with the
   legend below "Sin dato" — visually distinct from a zero bar.
   Under the chart, a thin overlay line or ghost bars showing the comparison month
   (mayo) in light gray, with a small legend: "■ Junio 2026  ░ Mayo 2026".
4. Anomaly alert card (amber/warning style, light #fff3cd background, alert-triangle
   icon): title "Consumo inusual el jueves 5", body "Tu consumo fue 40% mayor a tu
   promedio diario." and an actionable tip line with a lightbulb icon: "Revisá si
   quedó algún equipo encendido más tiempo del habitual; identificarlo te ayuda a
   evitar repetirlo." Tip phrased as opportunity, not punishment.
5. Footer caption: "Datos disponibles hasta el 10/06/2026, 23:59".

Bottom navigation with "Consumo" tab active. Everything in kWh only.
```

---

### 4.6 · Consumo — detalle de día (drill-down) — *Mobile*

```text
SCREEN: Day detail (drill-down from the daily chart)

Design the mobile day-detail screen the user reaches by tapping one bar (day) in the
monthly consumption chart. There is NO hourly breakdown — daily total is the maximum
granularity.

Top bar: back arrow ("Volver a junio 2026"), title "Jueves 5 de junio".

1. Hero card: big figure in Space Grotesk "11,2 kWh" with label "Consumo del día".
2. Context rows inside the same card:
   - "Tu promedio diario de junio: 7,8 kWh" with an amber chip "↑ 40%".
   - "Mismo día de la semana pasada: 7,5 kWh".
3. Anomaly explanation card (warning style): "Este día tu consumo fue 40% mayor a tu
   promedio diario." plus actionable tip with lightbulb icon: "Identificar qué pasó
   ese día te ayuda a planificar mejor tu consumo."
4. Mini context chart: the month's daily bars in miniature with day 5 highlighted,
   as orientation of where this day sits in the month.
5. Footer caption: "Datos disponibles hasta el 10/06/2026, 23:59".

Clean, focused, single-day reading. Decimal comma (Argentine format: "11,2 kWh").
```

---

### 4.7 · Consumo — versión desktop (alta densidad) — *Desktop / Web*

```text
SCREEN: Consumption analysis — desktop web version (high density)

Design the DESKTOP web version of the consumption analysis screen. This is where
high-density features live: multi-period analysis and CSV export.

Layout: fixed left sidebar (dark green #124e2f) with the EPEC logo on top and nav
items with Lucide icons: "Inicio", "Consumo" (active, lighter green highlight),
"Objetivos", "Factura", and at the bottom "Notificaciones" and "Configuración".
Main content area on light gray #f5f7f6 background.

Header row: page title "Consumo", date-range picker ("01/04/2026 – 10/06/2026"),
and an outlined button with download icon: "Exportar CSV".

1. Wide card — daily bar chart spanning the selected multi-month range, green bars,
   Y axis "kWh", with month separators. Comparison overlay of the same period last
   year in light gray. Legend: "■ 2026  ░ 2025".
2. Row of 3 KPI cards: "Total del período: 412 kWh" · "Promedio diario: 7,9 kWh" ·
   "Día de mayor consumo: 5 de junio · 11,2 kWh".
3. Side-by-side comparison table card, "Comparación por mes": columns
   "Mes | Consumo (kWh) | vs. mes anterior | vs. año anterior", rows for Abril, Mayo,
   Junio (parcial). Compact bordered table, striped rows, direction arrows with
   green/amber chips in the delta columns.
4. Anomaly alert strip (amber) above the footer: "Consumo inusual el jueves 5 de
   junio: 40% sobre tu promedio diario." + tip link "Ver detalle del día".
5. Footer caption: "Datos disponibles hasta el 10/06/2026, 23:59 · Última
   actualización: 11/06/2026, 06:15".

Dense but ordered, utility-grade data UI. Only kWh, no money.
```

---

### 4.8 · Objetivos de consumo — *Mobile*

```text
SCREEN: Consumption goals (Objetivos)

Design the mobile goals screen with three indicators stacked as cards.

Top bar: green, title "Objetivos", bell and settings icons.
Header card: "Tu objetivo de junio: 210 kWh" with an edit (pencil) link "Editar".

Card 1 — "Tu objetivo vs. tu zona":
- Two labeled horizontal bars: "Tu objetivo: 210 kWh" (green bar) and "Promedio de
  tu zona: 215 kWh" (gray bar, slightly longer).
- Caption: "Tu objetivo es 2% menor que el promedio de tus vecinos en un radio
  de 150 m."

Card 2 — "Ritmo de consumo" (days-of-goal consumed):
- A horizontal progress bar showing goal consumption pace: marker for "Días
  transcurridos: 11" and fill representing "Días de objetivo consumidos: 11,1".
- Status line in neutral/positive tone: "Vas en línea con tu objetivo."
- Secondary caption: "Consumiste el equivalente a 11,1 días de tu objetivo en 11 días."

Card 3 — "Consumo diario vs. objetivo":
- Small daily bar chart of the last 7 days in green with a horizontal dashed
  reference line labeled "Objetivo diario: 7 kWh".
- Caption: "Ayer: 6,4 kWh · 0,6 kWh por debajo de tu objetivo diario."

Footer caption: "Datos disponibles hasta el 10/06/2026, 23:59".
Bottom navigation with "Objetivos" tab active. Only kWh, no money.

ALTERNATE STATE to also design (same screen, saturated goal): progress bar of Card 2
full at 100% in amber, status text "Ya alcanzaste tu objetivo de consumo de este mes."
plus line "Excedente: 14 kWh" and actionable tip: "Pequeños ajustes en lo que queda
del mes pueden moderar el excedente: priorizá los equipos de mayor consumo."
```

---

### 4.9 · Mi Factura — *Mobile*

```text
SCREEN: My bill (Mi Factura)

Design the mobile bill section. CRITICAL: this screen explains bill concepts but
shows NO amounts, NO prices, NO money — the official bill lives on EPEC's website.

Top bar: green, title "Mi Factura", bell and settings icons.

1. Intro line: "Entendé qué significa cada concepto de tu factura. Para verla,
   descargarla o pagarla, te llevamos al sitio oficial de EPEC."

2. Card "¿Qué compone tu factura?" — an accordion list of 5 concept rows, each with
   a Lucide icon, a title and one explanatory sentence (no numbers):
   - "Energía" (zap icon): "Lo que consumiste en el período, medido en kWh."
   - "Transporte" (cable/tower icon): "El costo de llevar la energía desde donde se
     genera hasta tu zona."
   - "Distribución (VAD)" (network icon): "El valor agregado de distribución: mantener
     y operar la red que llega hasta tu casa."
   - "Cargo fijo" (file-text icon): "Un cargo por disponer del servicio,
     independiente de tu consumo."
   - "Impuestos" (landmark icon): "Tributos nacionales, provinciales y municipales
     que se aplican sobre el servicio."
   First row ("Energía") shown expanded, the rest collapsed.

3. Card "Ver, descargar y pagar tu factura":
   - Two inputs: "Número de cliente" (placeholder "1109294") and "Número de contrato"
     (placeholder "0281767003"), numeric, in Space Grotesk.
   - Helper caption: "Encontrás ambos números en la parte superior de tu factura."
   - Full-width primary green button with external-link icon: "Ir a mi factura en
     el sitio de EPEC".
   - Error state visible on the second input: empty field with red border and helper
     text "Ingresá tu número de contrato para continuar."

4. Info banner (light blue info style, bell icon): "Te avisaremos por notificación
   y por correo cuando tu factura esté por vencer."

Bottom navigation with "Factura" tab active.
```

---

### 4.10 · Notificaciones (centro) — *Mobile*

```text
SCREEN: Notifications center

Design the mobile notifications inbox.

Top bar: back arrow, title "Notificaciones", and a settings gear shortcut on the
right that leads to notification preferences.

List of notification cards grouped under date headers ("Hoy", "Esta semana",
"Anteriores"). Each card: leading icon in a tinted circle, title, one body line,
timestamp, unread dot for new items. Exactly these 3 notification types exist:

1. (Hoy, unread) Bill available — receipt icon, blue info tint:
   "Tu factura ya está disponible" / "Podés verla, descargarla y pagarla en el sitio
   de EPEC." / "11/06/2026, 08:00".
2. (Esta semana, unread) Anomalous consumption — alert-triangle icon, amber tint:
   "Consumo inusual el jueves 5" / "Tu consumo fue 40% mayor a tu promedio diario.
   Mirá el detalle del día." / "06/06/2026, 07:30".
3. (Anteriores, read) Due date reminder — calendar-clock icon, amber tint:
   "Tu factura vence pronto" / "Vence el 28/05/2026. Accedé al sitio de EPEC para
   pagarla." / "25/05/2026, 09:00".

Include one older read notification of type 1 to fill the "Anteriores" group.
No outage or claims notifications exist in this product. Empty-state hint at the
bottom: "No tenés más notificaciones."
```

---

### 4.11 · Configuración de notificaciones — *Mobile*

```text
SCREEN: Notification preferences

Design the mobile notification-preferences screen with granular toggles.

Top bar: back arrow, title "Configuración de notificaciones".

1. Intro caption: "Elegí qué avisos querés recibir. Buscamos ser relevantes, no
   frecuentes."

2. Section "Notificaciones push" — a card with 3 toggle rows, each with icon, title,
   description and a switch (green when on):
   - "Factura disponible" (receipt icon) — "Cuando tu factura esté lista en el sitio
     de EPEC." — ON
   - "Vencimiento próximo" (calendar-clock icon) — "Unos días antes de la fecha de
     vencimiento." — ON
   - "Consumo anómalo" (alert-triangle icon) — "Cuando un día supere claramente tu
     promedio diario." — ON

3. Section "Correo electrónico" — a card with 1 toggle row:
   - "Avisos de facturación por correo" (mail icon) — "Recibí también por email los
     avisos de factura disponible y vencimiento." — ON

4. Muted footnote at the bottom: "Aplicamos un límite interno de frecuencia para no
   sobrecargarte de avisos. Los avisos críticos, como el vencimiento de tu factura,
   nunca se suprimen."

Clean settings UI, generous touch targets, dividers between rows.
```

---

### 4.12 · Configuración general — *Mobile*

```text
SCREEN: Settings (Configuración)

Design the mobile general settings screen.

Top bar: back arrow, title "Configuración".

1. Profile header: avatar circle with initials "PB", name "Pedro Berecibar",
   caption "pedro@correo.com".

2. Section "Mi objetivo de consumo" — card:
   - Row showing current value: "Objetivo mensual" with figure "210 kWh"
     (Space Grotesk) and a chevron, tappable to edit.
   - Caption: "Sugerido para tu zona: 215 kWh". Link "Usar el sugerido".

3. Section "Datos de mi suministro" — card with two editable rows:
   - "Número de cliente" → "1109294"
   - "Número de contrato" → "0281767003"
   - Caption: "Se usan para llevarte a tu factura en el sitio de EPEC."

4. Section "Notificaciones" — single row with bell icon, "Configuración de
   notificaciones", chevron (links to the preferences screen).

5. Section "Privacidad" — card:
   - Toggle row: "Analítica avanzada" — "Permitir el uso de mis datos para análisis
     avanzados. Desactivado por defecto." — OFF (explicit opt-in).
   - Static row: "Comparaciones con tu zona" — caption "Los datos de tus vecinos se
     procesan de forma disociada: nunca identifican hogares individuales."

6. Bottom: outlined neutral button "Cerrar sesión", and version caption
   "EPEC Clientes · versión 1.0".

Institutional settings UI, list-style cards with 1px borders.
```

---

## 5. Checklist de verificación por pantalla

Validar cada generación de Stitch contra estas reglas antes de dar por buena la pantalla:

- [ ] **Sin dinero:** no aparece `$`, "pesos", precios ni montos en ningún lugar. La única unidad es **kWh** (W mayúscula, h minúscula).
- [ ] **Proyección como rango:** nunca un número exacto; siempre con la leyenda "Se ajusta a medida que avanza el mes".
- [ ] **Granularidad diaria:** ningún gráfico por hora, ni bandas horarias (Pico/Valle/Resto), ni cuenta regresiva.
- [ ] **Sin cortes ni reclamos:** no existen accesos, secciones ni notificaciones de cortes o reclamos.
- [ ] **Sin subsidio:** no hay barras de bloque subsidiado ni categorías N1/N2/N3.
- [ ] **Latencia declarada:** toda pantalla con datos de consumo muestra "Datos disponibles hasta …".
- [ ] **Mala noticia + palanca:** toda alerta o estado desfavorable incluye un consejo accionable en lenguaje de oportunidad.
- [ ] **Copy en español argentino**, sentence case, sin signos de exclamación, sin emoji.

---

## Apéndice A — Tokens para el theme de Stitch

| Token | Valor |
|---|---|
| Primary / brand | `#124e2f` |
| Brand hover | `#1a6640` · pressed `#0f3d24` |
| Tint suave (cards destacadas, hover) | `#edf5f0` |
| Tint selección | `#d4eedd` |
| Fondo de página | `#f5f7f6` |
| Superficie (cards) | `#ffffff` |
| Borde por defecto | `#d5ddd9` (1px) |
| Texto primario | `#111614` |
| Texto secundario | `#4a5550` · muted `#8f9c97` |
| Success | `#1d8348` (fondo `#d4edda`) |
| Warning | `#e6910a` (fondo `#fff3cd`) |
| Error | `#c0392b` (fondo `#fde8e8`) |
| Info | `#1565c0` (fondo `#dbeafe`) |
| Fuente UI | Roboto (400 / 500 / 700) |
| Fuente técnica (cifras kWh, datos) | Space Grotesk (400 / 500 / 600) |
| Tamaños | h1 34px · h2 28px · h3 24px · body 15px · label 13px · caption 11px |
| Radios | botones/inputs/cards 4px · paneles 6px · cards hero 8px |
| Sombra | `0 1px 4px rgba(0,0,0,0.08)` (muy sutil) |
| Grilla de espaciado | base 4px (4 · 8 · 12 · 16 · 24 · 32 · 48) |
| Iconos | Lucide, trazo fino, 24px |

## Apéndice B — Copy bank (textos obligatorios, usar verbatim)

**Leyendas transversales**
- "Se ajusta a medida que avanza el mes" (acompaña toda proyección).
- "Datos disponibles hasta el [fecha], 23:59" / "Última actualización: [fecha y hora]".
- "Consumo medido hasta ayer a las 23:59" (variante de latencia).

**Indicador 2 — textos dinámicos (Módulo 6, umbral ±5%)**
| Condición | Texto |
|---|---|
| Por debajo del ritmo objetivo (−5%) | "Vas bien, estás por debajo de tu ritmo objetivo." |
| Dentro de ±5% | "Vas en línea con tu objetivo." |
| Por encima del ritmo objetivo (+5%) | "Atención, estás consumiendo más rápido que tu objetivo." |
| Objetivo agotado antes de fin de mes | "Ya alcanzaste tu objetivo de consumo de este mes." (+ excedente en kWh + palanca accionable; indicador saturado al 100%) |

**Comparaciones del Home**
- "Este mes: [X] kWh · En [mes año anterior] llevabas [Y] kWh a esta altura"
- Refuerzo positivo de zona: "Consumís [N]% menos que el promedio de tus vecinos en un radio de 150 m."

**Estados vacíos**
- Sin histórico: "Aún no hay histórico comparable disponible."
- Datos insuficientes para proyectar: "Aún no hay datos suficientes para proyectar tu consumo."
