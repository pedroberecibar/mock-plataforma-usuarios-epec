# Plan de Refactorización de UI/UX — Frontend EPEC Clientes

> Autor: Claude Code · Fecha: 2026-06-22  
> Basado en auditoría completa de todas las pantallas y el DESIGN-SYSTEM-REFACTOR-SOLORA.md

---

## 1. Estado actual — diagnóstico por pantalla

### AppShell (`AppShell.tsx`)
- **Estado:** Bien. Sidebar verde `#124e2f` intocable, bottom nav mobile correcto, logo/usuario en sidebar.
- **Deuda:** No tiene top bar en mobile (solo bottom nav). Sin transiciones entre vistas. `display: "none"` para `.app-sidebar` / `.app-bottomnav` depende de clases CSS globales — no aislado.
- **Prioridad:** Media.

### LoginPage (`LoginPage.tsx`)
- **Estado:** Bien. Layout split (panel izquierdo verde + formulario), design tokens usados, responsivo con clase CSS.
- **Deuda:** `¡Bienvenido!` (violación de tono institucional). Loading spinner es solo texto "Ingresando…" sin feedback visual real.
- **Prioridad:** Baja (está bien para MVP).

### OnboardingObjetivoPage (`OnboardingObjetivoPage.tsx`)
- **Estado:** Funcional pero sin alineación visual con el design system.
- **Deuda:** Usa `color.white` (blanco puro) en vez de `bg.surface`; `color.neutral200` en vez de `border.default`; número kWh con `fontWeight.bold` en vez del hero style `fontWeight.light`; `¡Bienvenido!` con signo de exclamación; sin fuente `font.sans` en el wrapper; no usa tokens `fg.primary`/`fg.secondary` consistentemente; card de sugerido debería ser `cardFeaturedStyle` (`#F3EDE2`).
- **Prioridad:** Alta.

### HomePage (`HomePage.tsx`)
- **Estado:** Bien estructurado. Sticky header correcto. Grid auto-fit con 4 bloques.
- **Deuda:** Timestamp footer tiene `maxWidth` no centrado (falta `margin: "0 auto"`). Los bloques individuales (`BloqueConsumoMes`, `BloqueZona`, `BloqueProyeccion`, `BloqueAccesos`) no revisados — los números kWh pueden no ser heroes visuales suficientes (tamaño, peso).
- **Prioridad:** Media (verificar bloques individuales).

### ConsumoPage (`ConsumoPage.tsx`)
- **Estado:** Funciona, pero es la página con más deuda de diseño.
- **Deuda:**
  - `fontFamily: "sans-serif"` en el wrapper (hardcodeado, debe ser `font.sans`)
  - `maxWidth: 900` (inconsistente con las demás páginas)
  - No tiene `PageHeader` sticky (solo un `<div>` con `display: flex`)
  - `<h2>Mi Consumo</h2>` no usa `fontSize`/`fg.link` del design system
  - `StatCard` componente local con colores hardcodeados (`#fff`, `#E8DFD0`, `#6B5A45`, `#999`)
  - `StatsBarConsumo` con colores hardcodeados (`#b22c2c`, `#1a7a4a`, `#6B5A45`, `#333`)
  - `<h3>` de secciones hardcodeados (`fontSize: 16, color: "#333"`)
  - Anomaly banner no usa `cardAlertStyle`
  - Botón Exportar CSV oculto con `display: "none"` en el estilo inline (debería estar en media query)
- **Prioridad:** Alta (es la pantalla de más uso).

### ObjetivosPage (`ObjetivosPage.tsx`)
- **Estado:** Mayormente correcto con design tokens.
- **Deuda:** Encoding issues en comentarios (UTF-8 mojibake: `â€"`, `Ã©`, `â"€`). `pct` calculado de forma indirecta e inconsistente. El número objetivo `2.5rem` podría ser más prominente como hero visual. Sin `PageHeader` sticky consistente.
- **Prioridad:** Baja (funciona bien).

### FacturaPage (`FacturaPage.tsx`)
- **Estado:** Bien. Usa design tokens, accordion correcto.
- **Deuda:** Ninguna crítica.
- **Prioridad:** Baja.

### AlertasPage (`AlertasPage.tsx`)
- **Estado:** Bien. Usa design tokens, toggles correctos.
- **Deuda:** Ninguna crítica.
- **Prioridad:** Baja.

---

## 2. Arquitectura de información — qué mostrar en cada pantalla

### Login
- Logo EPEC prominente
- Campo: Número de Suministro (identificador único del cliente)
- Campo: Contraseña
- Feedback de error claro ("Usuario o contraseña incorrectos")
- **No mostrar:** versión, links de soporte, "¿Olvidó su contraseña?" (fuera de MVP)

### Onboarding (primer login)
- Mensaje de bienvenida institucional (sin exclamación)
- Número sugerido grande como hero (basado en vecinos del radio)
- Contexto del sugerido: "basado en N vecinos cercanos, mismo mes del año anterior"
- CTA principal: "Usar este objetivo"
- CTA secundario: "Ingresar mi objetivo"
- Fallback si no hay datos: ir directo al input manual con mensaje claro

### Home (dashboard)
Bloques en orden de prioridad visual:
1. **Consumo del mes** (hero card `#F3EDE2`): kWh acumulado a la fecha, comparación año anterior, comparación mes anterior. El número kWh es el elemento visual dominante (42px Space Grotesk 300).
2. **Comparación con tu zona**: posición relativa vs vecinos (badge verde/rojo con porcentaje).
3. **Proyección al cierre** (featured card): rango en kWh, leyenda "Se ajusta a medida que avanza el mes".
4. **Accesos directos**: botones hacia Factura y Objetivos.
5. **Timestamp**: fecha de última actualización de datos (extremo inferior, monospace pequeño).

### Consumo
Secciones en orden:
1. **Page header** sticky: título "Mi Consumo" + botón Exportar CSV (solo ≥768px).
2. **Cartel de latencia**: "Datos disponibles hasta [fecha]" (informativo, no alarmante).
3. **Banner anomalía** (condicional): "El [día] tu consumo fue X% mayor a tu promedio".
4. **Stats rápidos**: Día más alto, Día más bajo, Promedio diario, Tendencia 7d, Hora pico.
5. **Gráfico de barras diarias**: barras verdes con gradiente, barra anómala en amber, clic para drill-down.
6. **Panel detalle día** (al hacer clic en barra): kWh del día, comparación con promedio, gráfico horario.
7. **Comparación histórica**: mes actual vs mes anterior vs mismo mes año anterior.
8. **Comparación con vecinos**: posición relativa, objetivo diario de referencia.

### Objetivos
Secciones:
1. **Objetivo vigente**: número en kWh como hero (grande, Space Grotesk 300).
2. **Progreso acumulado**: barra verde/amber/rojo, porcentaje, texto contextual.
3. **Indicador 2 — Días**: mensaje dinámico (bajo_ritmo / en_ritmo / sobre_ritmo / agotado), barra de días.
4. **Indicador 3 — Diario**: consumo real ayer vs objetivo diario.
5. **Indicador 1 — Zona**: chip comparativo objetivo vs promedio zonal.
6. **Resumen del mes**: KPIs mini (promedio diario, kWh restantes, podés usar por día).
7. **Formulario**: modificar objetivo (input numérico + botón Guardar).

### Mi Factura
Secciones:
1. **Banner vencimiento** (condicional, si ≤5 días): alerta prominente con fecha exacta.
2. **Fecha de vencimiento** (si existe pero no urgente): texto informativo.
3. **Conceptos de tu factura**: acordeón con 5 conceptos (Energía, Transporte, VAD, Cargo fijo, Impuestos).
4. **Acceso a factura**: card con botón CTA "Ver mi factura" que abre portal EPEC.
5. **Nota**: "Te avisaremos por notificación cuando tu próxima factura esté disponible."

### Alertas
Secciones:
1. **Título y descripción** de la sección.
2. **Card agrupada** con 3 toggles:
   - Factura disponible
   - Vencimiento próximo
   - Consumo inusual
3. **Nota informativa**: "Los avisos se envían al correo asociado a tu cuenta."

---

## 3. Componentes compartidos que faltan

Antes de refactorizar páginas, crear estos componentes reutilizables:

| Componente | Descripción | Pantallas que lo usan |
|---|---|---|
| `PageHeader` | Sticky header con título de sección, slot de acciones opcionales | Home, Consumo, Objetivos, Factura, Alertas |
| `LoadingSkeleton` | Placeholder animado (shimmer) para estados de carga | Todas |
| `EmptyState` | Estado vacío con icono, mensaje, CTA opcional | Todas |
| `KwhHero` | Número kWh grande como hero (Space Grotesk, configurable en tamaño) | Home, Onboarding, Objetivos |
| `StatMiniCard` | Tarjeta pequeña de KPI con label, valor, sub | ConsumoPage (reemplaza StatCard local) |
| `AlertBanner` | Banner de alerta semántica (success/warning/error/info) con borde izquierdo | ConsumoPage, FacturaPage |
| `SectionTitle` | `<h3>` estilizado consistente para títulos de sección dentro de páginas | Todas |

---

## 4. Etapas del refactor

### Etapa 1 — Componentes base y tokens ✅ COMPLETADA (2026-06-22)
**Objetivo:** Crear la biblioteca de componentes reutilizables y verificar que la fuente Inter esté cargada.

**Archivos a crear/modificar:**
- `frontend/index.html` — verificar/actualizar Google Fonts con Inter variable + Space Grotesk
- `frontend/src/components/PageHeader.tsx` — nuevo
- `frontend/src/components/LoadingSkeleton.tsx` — nuevo
- `frontend/src/components/EmptyState.tsx` — nuevo
- `frontend/src/components/KwhHero.tsx` — nuevo
- `frontend/src/components/StatMiniCard.tsx` — nuevo
- `frontend/src/components/AlertBanner.tsx` — nuevo
- `frontend/src/components/SectionTitle.tsx` — nuevo

**Criterios de done:**
- `tsc --noEmit` limpio
- Los componentes renderizan correctamente en Storybook o en una página de prueba
- `PageHeader` tiene slot para actions (botones a la derecha)
- `KwhHero` acepta tamaño "hero" (42px), "card" (28px), "inline" (24px) como variantes
- `LoadingSkeleton` tiene animación shimmer suave

---

### Etapa 2 — AppShell: mobile top bar y transiciones ✅ COMPLETADA (2026-06-22)
**Objetivo:** Completar la shell de navegación para mobile y agregar transiciones suaves entre vistas.

**Archivos a modificar:**
- `frontend/src/components/AppShell.tsx`
- `frontend/src/App.tsx` (agregar transición de página)

**Cambios:**
- **Mobile top bar**: barra superior `#124e2f`, 60px, con logo EPEC (pequeño, izquierda), título de página activa (centro), sin acciones por ahora
- **Page title mapping**: objeto `{ home: "Inicio", consumo: "Mi Consumo", objetivos: "Objetivos", factura: "Mi Factura", alertas: "Alertas" }`
- **Transición entre vistas**: fade `opacity` 0→1 con 200ms ease-out al cambiar de vista
- **Dot indicator en bottom nav**: punto verde pequeño debajo del ítem activo (como spec Solora)
- En mobile: el contenido debe tener `paddingBottom: 60` para no quedar tapado por el bottom nav

**Criterios de done:**
- En viewport 375px se ve top bar verde con logo y título de página actual
- Al navegar entre secciones hay un fade suave
- El bottom nav muestra el dot indicator bajo el ítem activo
- No hay contenido tapado por el bottom nav

---

### Etapa 3 — OnboardingObjetivoPage: primera impresión del objetivo ✅ COMPLETADA (2026-06-22)
**Objetivo:** Hacer que la pantalla de onboarding siga el sistema visual warm y tenga el número kWh como hero.

**Archivos a modificar:**
- `frontend/src/pages/OnboardingObjetivoPage.tsx`

**Cambios:**
- Wrapper: `bg.page` como fondo, `font.sans`, padding generoso
- Mensaje: "Bienvenido" sin signo de exclamación
- Card de sugerido: `cardFeaturedStyle` (`#F3EDE2`, radius 20px, shadow warm)
- Número kWh: usar componente `KwhHero` variante "hero" (42px Space Grotesk 300)
- Texto de contexto: `fg.secondary`, `fontSize.sm`
- CTA principal: `brand.primary` con `radius.md` (12px)
- CTA secundario: outlined verde
- Estado sin datos: `EmptyState` con mensaje claro
- Estado loading: `LoadingSkeleton` de 1 card

**Criterios de done:**
- El número kWh dominante visualmente (42px)
- Card de sugerido visible en beige `#F3EDE2` (no blanco puro)
- Sin `color.white` hardcodeado
- Sin signos de exclamación en copys

---

### Etapa 4 — HomePage: bloques del dashboard ✅ COMPLETADA (2026-06-22)
**Objetivo:** Asegurar que el kWh del mes sea el hero visual de la pantalla principal, revisar los 4 bloques.

**Archivos a revisar/modificar:**
- `frontend/src/pages/HomePage.tsx` — ya bien estructurado, pequeños ajustes
- `frontend/src/components/BloqueConsumoMes.tsx`
- `frontend/src/components/BloqueZona.tsx`
- `frontend/src/components/BloqueProyeccion.tsx`
- `frontend/src/components/BloqueAccesos.tsx`

**Cambios:**
- `BloqueConsumoMes`: debe usar `cardFeaturedStyle` (`#F3EDE2`), el número kWh debe ser hero (42px `KwhHero`), comparaciones con badges semánticos (verde/rojo/amber)
- `BloqueProyeccion`: `cardFeaturedStyle`, rango en formato "198 – 226 kWh" prominente, leyenda "Se ajusta a medida que avanza el mes" en `fg.muted`
- `BloqueZona`: card estándar, badge de posición relativa
- `BloqueAccesos`: card estándar, 2 botones de navegación primarios
- `HomePage`: `maxWidth` del main debe estar en el `<div>` interior con `margin: "0 auto"`
- `PageHeader` en lugar del `<header>` inline actual

**Criterios de done:**
- `BloqueConsumoMes` tiene fondo beige `#F3EDE2` notoriamente distinto al fondo de página
- El número kWh del mes es el elemento visual más grande de la pantalla
- `BloqueProyeccion` tiene el mismo fondo featured o similar prominencia visual
- Grid funciona correctamente en 375px (1 col), 768px (2 col), 1280px+ (2-4 col)

---

### Etapa 5 — ConsumoPage: redesign completo de la pantalla central ✅ COMPLETADA (2026-06-22)
**Objetivo:** Eliminar toda la deuda de diseño de ConsumoPage y alinearlo completamente con el design system.

**Archivos a modificar:**
- `frontend/src/pages/ConsumoPage.tsx`
- `frontend/src/components/GraficoConsumoDiario.tsx`
- `frontend/src/components/PanelDetalleDia.tsx`
- `frontend/src/components/PanelComparacion.tsx`
- `frontend/src/components/PanelVecinosComparacion.tsx`
- `frontend/src/components/CartelLatencia.tsx`

**Cambios en `ConsumoPage.tsx`:**
- Wrapper: `fontFamily: font.sans`, `bg.page`, `maxWidth` alineado con el resto
- Reemplazar `<header>` inline por componente `PageHeader` (con botón CSV en el slot de acciones)
- `StatsBarConsumo` → usar componente `StatMiniCard` (eliminar el componente local `StatCard`)
- Los colores de tendencia: usar tokens del design system (no hardcoded `#b22c2c`)
- Títulos de sección `<h3>`: usar `SectionTitle`
- Anomaly banner: usar `AlertBanner` variante "warning"
- `display: "none"` en botón CSV: mover a media query CSS o estado responsive de React

**Cambios en componentes de gráfico:**
- `GraficoConsumoDiario`: aplicar `chartTheme` de `ChartTheme.ts` (gradiente en barras, warm tooltip, ejes warm)
- `PanelDetalleDia`: usar `cardFeaturedStyle` para el número kWh del día, `KwhHero` para el dato principal
- `PanelComparacion`: verificar que usa design tokens
- `CartelLatencia`: usar `AlertBanner` o una card info con borde izquierdo azul

**Criterios de done:**
- Cero colores hardcodeados en ConsumoPage.tsx (ni `#fff`, `#E8DFD0`, `#b22c2c`, etc.)
- Barra de gráfico usa gradiente verde `#227d50 → #124e2f`
- Barra anómala usa amber `#c0780a`
- Tooltip del gráfico tiene fondo warm `#F3EDE2`
- PanelDetalleDia muestra el kWh como hero visual

---

### Etapa 6 — ObjetivosPage: polish de indicadores ✅ COMPLETADA (2026-06-22)
**Objetivo:** Limpiar encoding issues, mejorar la jerarquía visual de los indicadores.

**Archivos a modificar:**
- `frontend/src/pages/ObjetivosPage.tsx`

**Cambios:**
- Eliminar todos los comentarios con encoding mojibake (borrar los comentarios o reescribirlos en inglés)
- El número objetivo vigente: aumentar a variante "hero" del `KwhHero` (actualmente `2.5rem` que es bien, confirmar que es Space Grotesk 300)
- El cálculo de `pct` simplificar y hacerlo más explícito (actualmente hay un cálculo indirecto de `dias_objetivo_consumidos * consumo_diario_objetivo_kwh`)
- `PageHeader` en lugar del `<h1>` + `<p>` actuales (consistencia con otras páginas)
- Verificar que `Card` interna usa `cardStyle` del design system (actualmente lo reimplementa inline)
- `MiniKpi` internamente consistente con `StatMiniCard`

**Criterios de done:**
- Sin mojibake en el archivo
- Número objetivo es prominente (hero visual)
- El cálculo de progreso es legible

---

### Etapa 7 — FacturaPage + AlertasPage: polish menor ✅ COMPLETADA (2026-06-22)
**Objetivo:** Pequeños ajustes para consistencia con el sistema visual actualizado.

**Archivos a modificar:**
- `frontend/src/pages/FacturaPage.tsx`
- `frontend/src/pages/AlertasPage.tsx`

**Cambios en FacturaPage:**
- `PageHeader` para reemplazar el `<h2>` de sección (y que la página tenga el mismo header sticky que las demás)
- El accordion: agregar hover state `bg.hover` al pasar el mouse (transición suave 150ms)
- Banner de vencimiento: usar `AlertBanner` variante "warning"
- Fecha de vencimiento informativa: usar `AlertBanner` variante "info" (borde azul)
- El botón "Ver mi factura": verificar que tiene `radius.md` (12px), hover state

**Cambios en AlertasPage:**
- `PageHeader` para reemplazar `<h2>` inline
- El `sectionHeaderStyle` ya usa `bg.muted` — verificar que no tiene border hard
- Toggle: la transición del thumb puede ser `motion.base` (250ms) en vez de `0.2s` hardcodeado

**Criterios de done:**
- `PageHeader` consistente en ambas páginas
- Hover en accordion items de FacturaPage
- AlertasPage sin cambios de comportamiento, solo polish

---

### Etapa 8 — Loading states, empty states y responsive QA ✅ COMPLETADA (2026-06-23)
**Objetivo:** Implementar loading skeletons reales, empty states visuales, y verificar responsividad en 375/768/1280px.

**Archivos a modificar/crear:**
- Todos los archivos de página (agregar skeletons)
- `frontend/src/components/LoadingSkeleton.tsx` (ya creado en Etapa 1, implementar variantes)

**Cambios:**
- Reemplazar todos los `<p>Cargando…</p>` por `LoadingSkeleton` apropiado para cada página:
  - Home: skeleton de 4 cards con shimmer
  - Consumo: skeleton de stats bar + chart placeholder (rectángulo animado)
  - Objetivos: skeleton de 1 card grande
  - Factura: skeleton de accordion items
  - Alertas: skeleton de 3 toggle rows
- `EmptyState` para casos donde no hay datos:
  - Consumo sin datos de serie
  - Objetivos sin datos de estado
- **Responsive QA**: con agent-browser, verificar 3 viewports: 375px, 768px, 1280px
  - Checklist: sin overflow horizontal, textos legibles, gráfico no truncado, botones con tamaño táctil ≥44px

**Criterios de done:**
- Ningún "Cargando…" de texto plano en la app
- Los empty states son visualmente coherentes y tienen mensaje claro
- No hay overflow horizontal en 375px
- Contenido no tapado por bottom nav en mobile

---

## 5. Orden de prioridad sugerido

| Etapa | Prioridad | Impacto visual | Complejidad |
|---|---|---|---|
| 1 — Componentes base | P0 (habilita todo lo demás) | Base | Baja |
| 5 — ConsumoPage | P1 (más deuda, más uso) | Alto | Alta |
| 3 — Onboarding | P1 (primera impresión post-login) | Alto | Baja |
| 2 — AppShell mobile | P1 (experiencia mobile) | Alto | Media |
| 4 — HomePage bloques | P2 | Alto | Media |
| 6 — ObjetivosPage | P2 | Medio | Baja |
| 7 — Factura+Alertas | P3 | Bajo | Baja |
| 8 — Loading+Responsive | P3 (quality gate) | Alto | Media |

---

## 6. Restricciones y reglas de oro

1. **kWh es la única unidad** — nunca $ ni pesos en ningún componente.
2. **Verde `#124e2f` en sidebar/top bar/CTAs/activos/positivos** — intocable como color base estructural.
3. **No blanco puro** — `bg.surface = #FDFCF9`, `bg.page = #F8F6F2`. Nunca `#ffffff` en superficies de app.
4. **No bordes en cards** — la separación es por contraste de superficie (warm-0 vs warm-1 vs warm-2).
5. **Inputs sí tienen borde** — `border.default = #D4C4A8` (cálido).
6. **TDD para componentes nuevos**: test primero para `PageHeader`, `LoadingSkeleton`, etc.
7. **Validar en browser con agent-browser** antes de reportar cada etapa como completa.
8. **No tocar tests existentes** mientras se refactorizan páginas — los tests verifican comportamiento, no estilos.

---

## 7. Checklist visual (aplicar a cada pantalla al terminar)

- [ ] Fondo de página es warm cream `#F8F6F2` (no blanco, no gris)
- [ ] Cards sin bordes explícitos (excepto inputs/alertas semánticas)
- [ ] Card hero/featured con fondo beige `#F3EDE2`
- [ ] Número kWh principal es el elemento visual más grande (≥36px, Space Grotesk 300)
- [ ] `PageHeader` sticky en todas las páginas del AppShell
- [ ] Radii generosos (≥12px en botones/inputs, ≥16px en cards)
- [ ] Verde EPEC solo en: sidebar, top bar, CTAs, activos, indicadores positivos
- [ ] Sombras sutiles y warm (sin `rgba(0,0,0,...)` puro)
- [ ] `font.sans` en todo el texto (no `"sans-serif"` hardcodeado)
- [ ] Ningún color hexadecimal hardcodeado fuera de `design-tokens.ts`
- [ ] Tono institucional: sin `¡` ni `!` en textos de la app

---

*Fin del plan — actualizar sección de estado de cada etapa al completarla.*
