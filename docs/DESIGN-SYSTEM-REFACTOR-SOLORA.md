# DESIGN SYSTEM REFACTOR — EPEC × Solora

**Documento de especificación para migrar el design system de la Plataforma Clientes EPEC hacia la estética del dashboard Solora — Energy Monitoring Dashboard (Phenomenon Studio, Dribbble shot #27210300).**

> Autor: Claude Code · Fecha: 2026-06-19
> Verificado: el shot fue analizado directamente en Dribbble con agent-browser antes de escribir este documento.

**Nota importante:** Solora es un **light theme warm cream**, NO dark. Los fondos del case study de presentación en Dribbble son oscuros, pero el app en sí tiene fondos crema cálido con acento amber/dorado. Este documento refleja la estética real del producto.

> **Restricción crítica:** la paleta green corporativa EPEC (`#124e2f` y toda su escala), los logos y el tono de voz institucional son **intocables**.

---

## Índice

1. [Filosofía de diseño](#1-filosofía-de-diseño)
2. [Warmth System: de neutro-frío a crema cálido](#2-warmth-system-de-neutro-frío-a-crema-cálido)
3. [Paleta de color refactorizada](#3-paleta-de-color-refactorizada)
4. [Tipografía](#4-tipografía)
5. [Espaciado y layout](#5-espaciado-y-layout)
6. [Cards y contenedores](#6-cards-y-contenedores)
7. [Componentes UI](#7-componentes-ui)
8. [Iconografía](#8-iconografía)
9. [Visualización de datos / Gráficos](#9-visualización-de-datos--gráficos)
10. [Animaciones y transiciones](#10-animaciones-y-transiciones)
11. [Checklist de archivos a modificar](#11-checklist-de-archivos-a-modificar)
12. [Migración del Global Design Context de Stitch](#12-migración-del-global-design-context-de-stitch)
13. [Plan de implementación sugerido](#13-plan-de-implementación-sugerido)

---

## 1. Filosofía de diseño

### 1.1 El shift: de "institucional neutro" a "warm data-forward"

El design system actual de EPEC comunica **solidez institucional**: fondos gris-frío (`#f5f7f6`), blanco puro en cards, el verde corporativo como fondo estructural del sidebar. Es correcto para una intranet de gestión comercial, pero en una plataforma residencial produce distancia y frialdad.

Solora resuelve esto con elegancia: **usa el calor como lenguaje visual**. Fondos crema/arena, superficies warm-white, un acento amber que evoca energía solar. El resultado es una app que se siente orgánica, premium y accesible sin perder precisión técnica. Los datos son los heroes visuales; el fondo se retira para dejarlos hablar.

Para EPEC, la traducción es directa:
- El **amber/dorado de Solora** → el **verde `#124e2f` de EPEC** (mismo rol semántico: la energía, la acción, lo positivo)
- Los **fondos crema** de Solora → fondos crema con un **tinte verde apenas perceptible** que conecta con la identidad EPEC sin subrayarla
- La **jerarquía de datos prominentes** de Solora → los kWh como números hero, con el contexto en segundo plano

El shift de esta migración **no cambia el modo de color** (sigue siendo light). Cambia la **temperatura emocional**: de neutro-frío institucional a cálido-preciso residencial.

### 1.2 Keywords del nuevo Design System

1. **Warm-precise** — calidez orgánica que no sacrifica exactitud técnica
2. **Data-hero** — los números kWh son los elementos visuales más grandes y prominentes
3. **Borderless warmth** — separación de superficies por contraste de temperatura, no por bordes 1px
4. **Green-as-energy** — el verde EPEC como señal de acción y positividad, no como estructura
5. **Airy hierarchy** — espacio generoso entre bloques; cada dato respira

### 1.3 Qué cambia y qué no

| Dimensión | Estado actual | Estado objetivo |
|---|---|---|
| Modo de color | Light neutro-frío | Light warm cream |
| Fondo de página | `#f5f7f6` (gris levemente verdoso-frío) | `#F8F6F2` (crema cálido, muy sutil) |
| Superficies card | `#ffffff` (blanco puro) | `#FDFCF9` (warm white) |
| Card hero/featured | igual a surface | `#F3EDE2` (beige visible — como las cards destacadas de Solora) |
| Verde EPEC | Fondo estructural (sidebar, top bar) | Señal y acción — se mantiene en sidebar/top bar + acento |
| Bordes de cards | `1px solid #d5ddd9` | Ninguno — contraste de superficie |
| Border radius | 4–8px | 12–20px |
| Números kWh | Funcionales, mismo peso que el texto | Heroes visuales: grandes, prominentes, Space Grotesk |
| Sombras | `rgba(0,0,0,0.08)` casi invisible | Levemente más pronunciadas con tinte warm |
| Tipografía | Roboto / Hanken Grotesk | Inter (variable) + Space Grotesk (datos) |
| Spacing | Denso (4px base, compacto) | Generoso (misma base, padding aumentado) |

---

## 2. Warmth System: de neutro-frío a crema cálido

### 2.1 El principio central

Solora no usa blanco puro ni gris neutro en ninguna superficie del app. Todo tiene un leve tinte cálido (amarillo-beige) que produce la sensación orgánica y premium. Para EPEC, el equivalente es un tinte verdoso-cálido, casi imperceptible en el fondo pero presente.

La regla: **ninguna superficie en el nuevo sistema es blanco puro `#ffffff` ni gris neutro**. Todo está levemente desplazado hacia el warm.

### 2.2 Sistema de capas de superficie (Warm Surface Layer System)

```css
/* Capas de superficie — separación por temperatura, no por bordes */
--warm-0: #F8F6F2;   /* page background — crema muy sutil */
--warm-1: #FDFCF9;   /* card standard — warm white */
--warm-2: #F3EDE2;   /* card featured / highlighted — beige visible (Solora-like) */
--warm-3: #E8DFD0;   /* selected state / active background */
--warm-4: #D4C4A8;   /* separador cálido — solo si necesario */
```

El contraste entre `--warm-0` (fondo) y `--warm-1` (card) es muy sutil pero suficiente para separar sin bordes. Entre `--warm-0` y `--warm-2` el contraste es notorio — usarlo para cards que merecen destacar (Proyección, Objetivo).

### 2.3 Cómo el verde EPEC funciona en el warm theme

En el sistema actual, el verde ocupa grandes áreas estructurales (toda la barra del sidebar). En el nuevo sistema, el verde sigue en el sidebar y top bar (identidad corporativa inamovible), pero como **acento de señal** en el resto del UI:

| Contexto | Uso actual del verde | Nuevo uso |
|---|---|---|
| Sidebar background | Fondo sólido `#124e2f` | Se mantiene igual |
| Top bar (mobile) | Fondo sólido `#124e2f` | Se mantiene igual |
| Botón primario CTA | Fondo `#124e2f` | Se mantiene igual |
| Links | `#1a6640` | `#124e2f` — más visible |
| Hover de nav | overlay verde | `rgba(18,78,47,0.08)` — más suave |
| Cards destacadas | `#edf5f0` (light green tint) | `#F3EDE2` (warm beige — como Solora) |
| Barras de gráfico | Verde sólido | Verde con gradiente sutil |
| Active nav indicator | Pill verde | Se mantiene, levemente más generoso |

---

## 3. Paleta de color refactorizada

### 3.1 Paleta base — Green EPEC: sin cambios

```css
/* INTOCABLE — verde corporativo EPEC, líneas 12-24 de colors_and_type.css */
--color-green-900: #0a2e1b;
--color-green-800: #0f3d24;
--color-green-700: #124e2f;   /* BRAND PRIMARY */
--color-green-600: #1a6640;
--color-green-500: #227d50;
--color-green-400: #3a9e6e;
--color-green-300: #6dbf97;
--color-green-200: #a8d9c0;
--color-green-100: #d4eedd;
--color-green-50:  #edf5f0;
```

### 3.2 Neutral Scale → Warm Neutral Scale

La escala neutral actual es fría (con tinte gris-verdoso-frío). Se reemplaza por una escala cálida que acompaña el nuevo sistema de superficies.

**Archivo:** `docs/EPEC Design System/colors_and_type.css`, líneas 26-35

| Token | Valor actual (frío) | 🔴 Valor nuevo (cálido) | Rol |
|---|---|---|---|
| `--color-neutral-900` | `#111614` | `#1C1410` | Texto primario — near-black cálido |
| `--color-neutral-800` | `#1e2421` | `#2E231A` | Texto muy oscuro |
| `--color-neutral-700` | `#2f3733` | `#4A3D2E` | Texto secundario dark |
| `--color-neutral-600` | `#4a5550` | `#6B5A45` | Texto secundario medium |
| `--color-neutral-500` | `#6b7772` | `#8C7A63` | Texto muted / placeholder |
| `--color-neutral-400` | `#8f9c97` | `#B0A090` | Texto terciario, íconos muted |
| `--color-neutral-300` | `#b5bfbb` | `#D4C4A8` | Separador warm |
| `--color-neutral-200` | `#d5ddd9` | `#E8DFD0` | Borde muy suave si necesario |
| `--color-neutral-100` | `#eaeeec` | `#F3EDE2` | Surface elevated / featured card |
| `--color-neutral-50`  | `#f5f7f6` | `#F8F6F2` | Page background |
| `--color-white`       | `#ffffff` | `#FDFCF9` | Warm white — card surface |

### 3.3 🟢 Nueva paleta Warm Surface (agregar en colors_and_type.css)

```css
/* WARM SURFACE PALETTE — agregar después del neutral scale */
--warm-0: #F8F6F2;   /* page background */
--warm-1: #FDFCF9;   /* card standard */
--warm-2: #F3EDE2;   /* card featured (highlighted card — como Solora) */
--warm-3: #E8DFD0;   /* selected / active background */
--warm-4: #D4C4A8;   /* separador warm, solo si necesario */
--warm-text-1: #1C1410;  /* texto primario — near-black cálido */
--warm-text-2: #6B5A45;  /* texto secundario */
--warm-text-3: #8C7A63;  /* texto muted */
```

### 3.4 Semantic UI Tokens — REEMPLAZAR

**Archivo:** `docs/EPEC Design System/colors_and_type.css`, líneas 53-80

```css
/* 🔴 REEMPLAZAR semantic UI tokens */

/* Backgrounds */
--bg-page:         var(--warm-0);           /* #F8F6F2 */
--bg-surface:      var(--warm-1);           /* #FDFCF9 */
--bg-surface-feat: var(--warm-2);           /* #F3EDE2 — card destacada (Solora-style) */
--bg-sidebar:      var(--color-green-700);  /* #124e2f — intocable */
--bg-header:       var(--color-green-700);  /* #124e2f — intocable */
--bg-hover:        rgba(18,78,47,0.06);     /* verde muy sutil en hover */
--bg-selected:     var(--warm-3);           /* #E8DFD0 */
--bg-muted:        var(--warm-2);           /* #F3EDE2 */

/* Foregrounds */
--fg-primary:     var(--warm-text-1);   /* #1C1410 */
--fg-secondary:   var(--warm-text-2);   /* #6B5A45 */
--fg-muted:       var(--warm-text-3);   /* #8C7A63 */
--fg-on-dark:     var(--color-white);   /* sin cambio */
--fg-link:        var(--color-green-700); /* #124e2f */
--fg-link-hover:  var(--color-green-600); /* #1a6640 */

/* Borders — mínimos, solo cuando el contraste de superficie no alcanza */
--border-default: var(--warm-4);          /* #D4C4A8 — cálido, no gris */
--border-strong:  var(--color-neutral-300); /* #D4C4A8 */
--border-focus:   var(--color-green-600); /* #1a6640 */
--border-brand:   var(--color-green-700); /* #124e2f */

/* Brand */
--brand-primary:  var(--color-green-700); /* sin cambio */
--brand-hover:    var(--color-green-600); /* sin cambio */
--brand-pressed:  var(--color-green-800); /* sin cambio */
```

### 3.5 Paleta semántica — ajuste al warm

Los colores semánticos se mantienen numéricamente pero con fondos warm en lugar de fondos fríos:

| Rol | Color texto/ícono | 🔴 Fondo badge nuevo |
|---|---|---|
| Success | `#1d8348` (sin cambio) | `rgba(18,78,47,0.10)` — warm green tint |
| Warning | `#e6910a` (sin cambio) | `rgba(230,145,10,0.10)` |
| Error | `#c0392b` (sin cambio) | `rgba(192,57,43,0.08)` |
| Info | `#1565c0` (sin cambio) | `rgba(21,101,192,0.08)` |

```css
/* 🟢 Agregar después de las semantic status colors */
--color-success-bg-warm:  rgba(18,78,47,0.10);
--color-warning-bg-warm:  rgba(230,145,10,0.10);
--color-error-bg-warm:    rgba(192,57,43,0.08);
--color-info-bg-warm:     rgba(21,101,192,0.08);
```

### 3.6 Chart Colors — paleta para gráficos en light warm

```css
/* 🟢 CHART PALETTE — Light warm background */
--chart-primary:      #1a6640;   /* barras principales — verde EPEC legible en warm */
--chart-primary-dim:  rgba(26,102,64,0.30);  /* barras dimmed / comparación */
--chart-comparison:   rgba(180,175,170,0.40); /* overlay período anterior — warm gray */
--chart-anomaly:      #c0780a;   /* barra anómala — amber oscuro (cálido, no rojo) */
--chart-goal-line:    rgba(18,78,47,0.50);   /* reference line objetivo */
--chart-grid:         rgba(180,170,155,0.30); /* grid lines — warm, suaves */
--chart-axis-text:    #8C7A63;               /* ejes — warm muted */
--chart-tooltip-bg:   #F3EDE2;               /* tooltip — warm-2 surface */
--chart-tooltip-border: #D4C4A8;             /* borde del tooltip */
```

### 3.7 Tokens TypeScript — design-tokens.ts

**Archivo:** `frontend/src/design-tokens.ts`

```typescript
// 🔴 REEMPLAZAR export const bg (líneas 74-82)
export const bg = {
  page:         "#F8F6F2",              // warm cream — page background
  surface:      "#FDFCF9",             // warm white — card standard
  surfaceFeat:  "#F3EDE2",             // beige visible — card destacada (Solora-style)
  selected:     "#E8DFD0",             // warm selected state
  sidebar:      color.green700,        // #124e2f — intocable
  header:       color.green700,        // #124e2f — intocable
  hover:        "rgba(18,78,47,0.06)", // hover verde muy sutil
  muted:        "#F3EDE2",             // warm muted bg
} as const;

// 🔴 REEMPLAZAR export const fg (líneas 84-91)
export const fg = {
  primary:   "#1C1410",   // near-black cálido
  secondary: "#6B5A45",   // warm brown-gray
  muted:     "#8C7A63",   // warm muted
  onDark:    "#ffffff",   // sin cambio
  link:      color.green700,   // #124e2f
  linkHover: color.green600,   // #1a6640
} as const;

// 🔴 REEMPLAZAR export const border (líneas 93-98)
export const border = {
  default: "#D4C4A8",       // warm separator — solo cuando necesario
  strong:  "#B0A090",       // warm border fuerte
  focus:   color.green600,  // #1a6640 — focus ring
  brand:   color.green700,  // #124e2f
} as const;

// 🟢 AGREGAR después de border
export const warmSurface = {
  0: "#F8F6F2",   // page
  1: "#FDFCF9",   // card
  2: "#F3EDE2",   // featured card
  3: "#E8DFD0",   // selected
  4: "#D4C4A8",   // separator
} as const;

export const chartColor = {
  primary:     "#1a6640",
  primaryDim:  "rgba(26,102,64,0.30)",
  comparison:  "rgba(180,175,170,0.40)",
  anomaly:     "#c0780a",
  goalLine:    "rgba(18,78,47,0.50)",
  grid:        "rgba(180,170,155,0.30)",
  axisText:    "#8C7A63",
  tooltipBg:   "#F3EDE2",
  tooltipBorder: "#D4C4A8",
} as const;
```

---

## 4. Tipografía

### 4.1 Font family — recomendación

**Recomendación: Inter (variable) como sans principal**, Space Grotesk se mantiene para datos kWh.

**Justificación frente a Roboto/Hanken Grotesk:**
- Inter tiene soporte de optical size axis: el grosor de trazo se ajusta automáticamente según el tamaño, lo que produce excelente legibilidad en 11–13px (labels, captions) sin ajustes manuales de peso
- En warm light backgrounds, Inter con optical sizing tiene mayor presencia y precisión que Roboto
- Variable font: un solo request HTTP para todos los pesos y estilos
- Solora usa una sans geométrica similar en espíritu

**Si el equipo prefiere mantener Hanken Grotesk:** es aceptable para la migración inicial. Hanken ya está en producción y es buena fuente. Inter puede quedar como mejora en Sprint de hardening.

### 4.2 Font import — actualizar

**Archivo:** `frontend/index.html`

```html
<!-- 🔴 REEMPLAZAR el link de Google Fonts existente -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300..700;1,14..32,300..700&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
```

**Archivo:** `docs/EPEC Design System/colors_and_type.css`, línea 6:

```css
/* 🔴 REEMPLAZAR el @import */
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300..700;1,14..32,300..700&family=Space+Grotesk:wght@400;500;600&display=swap');
```

### 4.3 Font tokens

**Archivo:** `docs/EPEC Design System/colors_and_type.css`, líneas 87-88:

```css
/* 🔴 REEMPLAZAR */
--font-sans:      'Inter', 'Segoe UI', system-ui, sans-serif;
--font-technical: 'Space Grotesk', 'Inter', sans-serif;
--font-mono:      'JetBrains Mono', 'Roboto Mono', monospace;
```

**Archivo:** `frontend/src/design-tokens.ts`, líneas 115-119:

```typescript
// 🔴 REEMPLAZAR
export const font = {
  sans:      "'Inter', 'Segoe UI', system-ui, sans-serif",
  technical: "'Space Grotesk', 'Inter', sans-serif",
  mono:      "'JetBrains Mono', 'Roboto Mono', monospace",
} as const;
```

### 4.4 KWH como hero visual — la mayor diferencia con el DS actual

La observación más importante de Solora: **los números de energía son el elemento visual más grande y prominente de cada pantalla**. El `860 Wh` o `20.6 kWh` domina el espacio de la card, con el label de contexto pequeño arriba o abajo.

```css
/* 🟢 AGREGAR — roles semánticos de KWH display */
--kwh-hero-size:    var(--text-4xl);     /* 42px — número principal de pantalla */
--kwh-hero-weight:  var(--weight-light); /* 300 — elegante, no pesado */
--kwh-hero-font:    var(--font-technical); /* Space Grotesk */
--kwh-hero-leading: 1.0;                 /* muy tight — solo el número */

--kwh-card-size:    var(--text-2xl);     /* 28px — número en card secundaria */
--kwh-card-weight:  var(--weight-regular); /* 400 */

--kwh-inline-size:  var(--text-xl);      /* 24px — número en contexto inline */
--kwh-inline-weight: var(--weight-medium); /* 500 */
```

### 4.5 Escala tipográfica completa — ajustar letter-spacing para warm

En backgrounds cálidos, un tracking ligeramente positivo mejora la legibilidad:

**Archivo:** `docs/EPEC Design System/colors_and_type.css`, líneas 113-117:

```css
/* 🔴 AJUSTAR letter spacing */
--tracking-tight:   -0.02em;
--tracking-normal:   0.01em;   /* leve positivo en light warm — más legible */
--tracking-wide:     0.04em;
--tracking-widest:   0.10em;
--tracking-caps:     0.08em;   /* 🟢 nuevo — labels uppercase */
```

---

## 5. Espaciado y layout

### 5.1 Spacing scale — misma base, nuevos valores semánticos

La escala 4px se mantiene. Cambia el **uso semántico**: el padding de cards pasa de denso a generoso, como en Solora.

**Archivo:** `docs/EPEC Design System/colors_and_type.css`, líneas 162-171:

```css
/* Base scale sin cambio — agregar escalones superiores */
--space-1:  4px;
--space-2:  8px;
--space-3:  12px;
--space-4:  16px;
--space-5:  20px;
--space-6:  24px;
--space-8:  32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
--space-20: 80px;
/* 🟢 nuevos */
--space-24: 96px;
--space-32: 128px;
```

### 5.2 Cambios de uso semántico de espaciado

| Elemento | Actual | 🔴 Nuevo |
|---|---|---|
| Padding card estándar | `space[6]` = 24px | `space[8]` = 32px |
| Padding card featured (hero) | `space[6]` = 24px | `space[10]` = 40px |
| Gap entre cards | `space[4]` = 16px | `space[6]` = 24px |
| Gap entre secciones de página | `space[6]` = 24px | `space[8]–[10]` = 32–40px |
| Padding lateral página mobile | `space[4]` = 16px | `space[5]` = 20px |
| Padding lateral página desktop | `space[6]` = 24px | `space[10]` = 40px |
| Height top bar mobile | 56px | 60px |
| Height bottom nav | 56px | 60px |

### 5.3 Grid system

**Mobile (375–767px):** 1 columna, padding lateral 20px, gap entre cards 24px.

**Tablet (768–1279px):** 2 columnas, gutter 24px, padding lateral 32px. Hero card ocupa las 2 columnas.

**Desktop (1280px+):** Sidebar fijo 240px + área principal. Área principal: padding 40px, máx 1120px de contenido. Cards en 12 columnas, gutter 24px.

---

## 6. Cards y contenedores

### 6.1 Eliminar bordes 1px en cards — principio central

Solora no usa bordes 1px en sus cards. La separación se logra por la diferencia entre `--warm-0` (fondo) y `--warm-1` (card). Este es el cambio visual más inmediato del refactor.

**Excepciones donde los bordes se mantienen:**
1. Inputs/formularios: `1px solid var(--border-default)` — necesario para indicar interactividad
2. Focus rings: `2px solid var(--border-focus)` — accesibilidad
3. Cards de alerta semántica: borde izquierdo `3px` en el color del status
4. Dividers de sección: `1px solid var(--warm-4)` cuando el contraste no alcanza

### 6.2 Border radius — nueva escala (Solora-inspired)

**Archivo:** `docs/EPEC Design System/colors_and_type.css`, líneas 177-182:

```css
/* 🔴 REEMPLAZAR toda la sección BORDER RADII */
--radius-xs:   4px;    /* badges inline, chips muy pequeños */
--radius-sm:   8px;    /* chips, pills, tags */
--radius-md:   12px;   /* inputs, botones, elementos interactivos */
--radius-lg:   16px;   /* cards estándar */
--radius-xl:   20px;   /* cards featured/hero, modales */
--radius-2xl:  24px;   /* containers grandes, login card */
--radius-full:  9999px; /* avatar, toggle, pill nav item */
```

**Archivo:** `frontend/src/design-tokens.ts`, líneas 167-175:

```typescript
// 🔴 REEMPLAZAR
export const radius = {
  xs:    4,
  sm:    8,
  md:    12,
  lg:    16,
  xl:    20,
  "2xl": 24,
  full:  9999,
} as const;
```

### 6.3 Shadow system — warm-tinted

Las sombras del nuevo sistema tienen un leve tinte warm (no shadow negro puro) para mantener coherencia con el sistema de color:

**Archivo:** `docs/EPEC Design System/colors_and_type.css`, líneas 187-192:

```css
/* 🔴 REEMPLAZAR */
--shadow-xs:  0 1px 2px rgba(100,80,60,0.06);
--shadow-sm:  0 1px 4px rgba(100,80,60,0.08), 0 1px 2px rgba(100,80,60,0.05);
--shadow-md:  0 4px 12px rgba(100,80,60,0.10), 0 1px 3px rgba(100,80,60,0.06);
--shadow-lg:  0 8px 24px rgba(100,80,60,0.12), 0 2px 6px rgba(100,80,60,0.07);
--shadow-xl:  0 20px 48px rgba(100,80,60,0.15), 0 4px 12px rgba(100,80,60,0.08);
/* 🟢 nuevo — sombra para card featured (como Solora) */
--shadow-warm: 0 8px 32px rgba(180,140,80,0.12), 0 2px 8px rgba(100,80,60,0.08);
```

### 6.4 Card variants — design-tokens.ts

**Archivo:** `frontend/src/design-tokens.ts`, líneas 191-198:

```typescript
// 🔴 REEMPLAZAR cardStyle
export const cardStyle: React.CSSProperties = {
  background:   bg.surface,              // #FDFCF9 warm white
  border:       "none",                  // sin borde — contraste de superficie
  borderRadius: `${radius.lg}px`,        // 16px
  boxShadow:    shadow.sm,
  padding:      `${space[8]}px`,         // 32px
  fontFamily:   font.sans,
} as const;

// 🟢 AGREGAR — card destacada (Solora-style: background beige visible)
export const cardFeaturedStyle: React.CSSProperties = {
  background:   bg.surfaceFeat,          // #F3EDE2 beige visible
  border:       "none",
  borderRadius: `${radius.xl}px`,        // 20px — más prominente
  boxShadow:    shadow.warm,
  padding:      `${space[10]}px`,        // 40px — más generoso
  fontFamily:   font.sans,
} as const;

// 🟢 AGREGAR — card de alerta semántica
export const cardAlertStyle = (
  variant: 'success' | 'warning' | 'error' | 'info'
): React.CSSProperties => ({
  background:   bg.surface,
  borderLeft:   `3px solid ${
    variant === 'success' ? color.green500 :
    variant === 'warning' ? '#e6910a' :
    variant === 'error'   ? '#c0392b' : '#1565c0'
  }`,
  borderRadius: `0 ${radius.lg}px ${radius.lg}px 0`,
  boxShadow:    shadow.xs,
  padding:      `${space[5]}px ${space[6]}px`,
  fontFamily:   font.sans,
}) as const;
```

---

## 7. Componentes UI

### 7.1 Buttons

**Primario — verde EPEC sobre warm background:**

```css
.btn-primary {
  background:    var(--color-green-700);    /* #124e2f */
  color:         var(--color-white);
  border:        none;
  border-radius: var(--radius-md);          /* 12px */
  font-family:   var(--font-sans);
  font-size:     var(--text-sm);            /* 13px */
  font-weight:   var(--weight-semibold);
  letter-spacing: var(--tracking-wide);
  padding:       12px 24px;
  transition:    background 200ms ease-in-out, box-shadow 200ms ease-in-out;
}
.btn-primary:hover {
  background: var(--color-green-600);       /* #1a6640 */
  box-shadow: var(--shadow-sm);
}
.btn-primary:active {
  background: var(--color-green-800);
  transform: scale(0.98);
  transition-duration: 80ms;
}
.btn-primary:focus-visible {
  outline: 2px solid var(--color-green-500);
  outline-offset: 2px;
}
```

**Secundario — outlined warm:**

```css
.btn-secondary {
  background:    transparent;
  color:         var(--color-green-700);
  border:        1px solid var(--color-green-700);
  border-radius: var(--radius-md);
  font-family:   var(--font-sans);
  font-size:     var(--text-sm);
  font-weight:   var(--weight-medium);
  padding:       11px 24px;
  transition:    background 200ms ease-in-out;
}
.btn-secondary:hover {
  background: rgba(18,78,47,0.06);
}
```

**Ghost — sobre warm surface:**

```css
.btn-ghost {
  background:    transparent;
  color:         var(--fg-secondary);       /* #6B5A45 */
  border:        none;
  border-radius: var(--radius-md);
  font-size:     var(--text-sm);
  font-weight:   var(--weight-medium);
  padding:       12px 24px;
  transition:    background 200ms ease-in-out, color 200ms ease-in-out;
}
.btn-ghost:hover {
  background: var(--warm-3);               /* #E8DFD0 */
  color: var(--fg-primary);
}
```

**Danger:**

```css
.btn-danger {
  background:    rgba(192,57,43,0.08);
  color:         #c0392b;
  border:        1px solid rgba(192,57,43,0.25);
  border-radius: var(--radius-md);
  font-size:     var(--text-sm);
  font-weight:   var(--weight-medium);
  padding:       11px 24px;
  transition:    background 200ms ease-in-out;
}
.btn-danger:hover {
  background: rgba(192,57,43,0.14);
}
```

### 7.2 Inputs / Forms

```css
.input {
  background:    var(--warm-1);             /* #FDFCF9 */
  border:        1px solid var(--warm-4);   /* #D4C4A8 — warm border */
  border-radius: var(--radius-md);          /* 12px */
  color:         var(--fg-primary);         /* #1C1410 */
  font-family:   var(--font-sans);
  font-size:     var(--text-base);
  padding:       12px 16px;
  transition:    border-color 200ms ease-in-out, box-shadow 200ms ease-in-out;
  width:         100%;
}
.input::placeholder {
  color: var(--warm-text-3);               /* #8C7A63 */
}
.input:hover {
  border-color: var(--color-neutral-300);  /* #D4C4A8 strong */
}
.input:focus {
  border-color: var(--color-green-600);   /* #1a6640 */
  box-shadow: 0 0 0 3px rgba(26,102,64,0.15);
  outline: none;
}
.input.error {
  border-color: #c0392b;
  box-shadow: 0 0 0 3px rgba(192,57,43,0.10);
}
.input-label {
  color:          var(--fg-secondary);     /* #6B5A45 */
  font-size:      var(--text-xs);
  font-weight:    var(--weight-medium);
  letter-spacing: var(--tracking-caps);
  text-transform: uppercase;
  margin-bottom:  6px;
}
/* Input técnico — Nº cliente, Nº contrato, kWh manual */
.input-technical {
  font-family:    var(--font-technical);   /* Space Grotesk */
  letter-spacing: 0.02em;
}
```

### 7.3 Data Tables

```css
.table-wrapper {
  background:    var(--warm-1);
  border-radius: var(--radius-lg);         /* 16px */
  overflow:      hidden;
  box-shadow:    var(--shadow-sm);
}
.table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-sans);
  font-size: var(--text-sm);
}
.table th {
  background:     var(--warm-2);           /* #F3EDE2 — warm header */
  color:          var(--fg-secondary);     /* #6B5A45 */
  font-size:      var(--text-xs);
  font-weight:    var(--weight-medium);
  letter-spacing: var(--tracking-caps);
  text-transform: uppercase;
  padding:        10px 16px;
  text-align:     left;
  border-bottom:  1px solid var(--warm-4);
}
.table td {
  color:         var(--fg-primary);
  padding:       12px 16px;
  border-bottom: 1px solid rgba(212,196,168,0.40); /* warm-4 con opacidad */
}
.table tr:nth-child(even) td {
  background: rgba(243,237,226,0.40);     /* warm-2 muy sutil */
}
.table tr:hover td {
  background: var(--bg-hover);            /* rgba(18,78,47,0.06) */
  transition: background 150ms ease-in-out;
}
.table td.numeric {
  font-family: var(--font-technical);
  text-align:  right;
}
```

### 7.4 Badges / Tags

```css
.badge {
  display:       inline-flex;
  align-items:   center;
  gap:           4px;
  padding:       3px 8px;
  border-radius: var(--radius-sm);        /* 8px */
  font-size:     var(--text-xs);
  font-weight:   var(--weight-medium);
  letter-spacing: 0.02em;
}
.badge-success { background: var(--color-success-bg-warm); color: #155a2e; }
.badge-warning { background: var(--color-warning-bg-warm); color: #7a4a00; }
.badge-error   { background: var(--color-error-bg-warm);   color: #7a1c1c; }
.badge-info    { background: var(--color-info-bg-warm);    color: #0d4272; }
.badge-neutral { background: var(--warm-2); color: var(--fg-secondary); }
.badge-brand   { background: var(--color-green-50); color: var(--color-green-700); }

/* Direction chips (↓ positivo, ↑ warning) */
.chip-down { background: var(--color-success-bg-warm); color: #155a2e; }
.chip-up   { background: var(--color-warning-bg-warm); color: #7a4a00; }
```

### 7.5 Progress Bars

```css
.progress-container {
  background:    var(--warm-3);           /* #E8DFD0 */
  border-radius: var(--radius-full);
  height:        8px;
  overflow:      hidden;
}
/* Default — verde (< 80% objetivo) */
.progress-fill {
  background:    linear-gradient(90deg, var(--color-green-700) 0%, var(--color-green-500) 100%);
  border-radius: var(--radius-full);
  height:        100%;
  transition:    width 600ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
/* Warning — amber (80–99% objetivo) */
.progress-fill.warning {
  background: linear-gradient(90deg, #d4850a 0%, #f0a930 100%);
}
/* Danger — rojo (≥ 100% objetivo) */
.progress-fill.danger {
  background: linear-gradient(90deg, #b02020 0%, #e05050 100%);
}
```

### 7.6 Toggles / Switches

```css
.switch-track {
  background:    var(--warm-4);           /* #D4C4A8 — off state warm */
  border-radius: var(--radius-full);
  width:         44px;
  height:        24px;
  transition:    background 200ms ease-in-out;
}
.switch-track.on {
  background: var(--color-green-600);    /* #1a6640 */
}
.switch-thumb {
  background:    #ffffff;
  border-radius: var(--radius-full);
  width:         20px;
  height:        20px;
  box-shadow:    var(--shadow-xs);
  transition:    transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
.switch-track.on .switch-thumb {
  transform: translateX(20px);
}
```

### 7.7 Navigation

**Bottom Nav (mobile):**

```css
.bottom-nav {
  background:   var(--color-green-700);   /* #124e2f — intocable */
  border-top:   none;
  height:       60px;
  padding-bottom: env(safe-area-inset-bottom);
}
.nav-item {
  color: rgba(255,255,255,0.55);
  transition: color 150ms ease-out;
}
.nav-item.active {
  color: #ffffff;
}
.nav-item-indicator {
  /* pill debajo del ícono activo */
  width: 4px; height: 4px;
  background: var(--color-green-300);    /* #6dbf97 */
  border-radius: var(--radius-full);
  margin: 2px auto 0;
}
.nav-item-label {
  font-size:      10px;
  font-weight:    var(--weight-medium);
  letter-spacing: 0.04em;
}
```

**Top Bar (mobile):**

```css
.top-bar {
  background: var(--color-green-700);    /* #124e2f — intocable */
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.top-bar-icon {
  color: rgba(255,255,255,0.80);
  transition: color 150ms ease-out;
}
.top-bar-icon:hover {
  color: #ffffff;
}
```

---

## 8. Iconografía

### 8.1 Mantener Lucide con stroke 1.5

Solora usa iconografía outlined de trazo fino, consistente con Lucide a `strokeWidth={1.5}`. No hay beneficio suficiente en migrar a Phosphor para este sprint. Se cambia únicamente el stroke width.

**Wrapper recomendado** para no tocar cada instancia:

```typescript
// 🟢 CREAR frontend/src/components/Icon.tsx
import type { LucideIcon } from 'lucide-react';

interface IconProps {
  icon: LucideIcon;
  size?: number;
  className?: string;
  color?: string;
}

export function Icon({ icon: IconComponent, size = 20, className, color }: IconProps) {
  return <IconComponent size={size} strokeWidth={1.5} className={className} color={color} />;
}
```

### 8.2 Tamaños y colores de íconos

| Contexto | Tamaño | Color |
|---|---|---|
| Nav bottom (mobile) | 22px | `rgba(255,255,255,0.55)` / `#ffffff` activo |
| Nav sidebar (desktop) | 20px | `rgba(255,255,255,0.60)` / `#ffffff` activo |
| Inline en body text | 16px | `var(--fg-muted)` |
| Button icon | 18px | hereda |
| Card leading icon | 20px | hereda del texto padre |
| Badge/chip icon | 14px | hereda |
| Hero/empty state | 48px | `var(--color-green-300)` |
| Alert leading icon | 20px | color del status |

---

## 9. Visualización de datos / Gráficos

### 9.1 Configuración global Recharts para warm light

**Archivo:** `frontend/src/components/charts/ChartTheme.ts` (crear)

```typescript
export const chartTheme = {
  barFill:         "#1a6640",
  barFillGradTop:  "#227d50",
  barFillGradBot:  "#124e2f",
  barFillDim:      "rgba(26,102,64,0.30)",
  barAnomaly:      "#c0780a",
  barComparison:   "rgba(180,175,170,0.40)",
  gridStroke:      "rgba(180,170,155,0.30)",
  gridStrokeDash:  "3 3",
  axisStroke:      "transparent",
  axisTickColor:   "#8C7A63",
  axisTickSize:    11,
  cursorFill:      "rgba(18,78,47,0.06)",
  refLineStroke:   "rgba(18,78,47,0.45)",
  refLineDash:     "6 4",
  refLineWidth:    1.5,
  tooltipBg:       "#F3EDE2",
  tooltipBorder:   "#D4C4A8",
  tooltipRadius:   12,
  tooltipTextPrimary: "#1C1410",
  tooltipTextSecondary: "#6B5A45",
  animationDuration: 600,
  animationEasing:   "ease-out",
} as const;
```

### 9.2 Gradiente en barras

```tsx
<defs>
  <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stopColor="#227d50" stopOpacity={0.90} />
    <stop offset="100%" stopColor="#124e2f" stopOpacity={0.70} />
  </linearGradient>
  <linearGradient id="barGradientAnomaly" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stopColor="#d4850a" stopOpacity={0.90} />
    <stop offset="100%" stopColor="#a06010" stopOpacity={0.70} />
  </linearGradient>
</defs>
```

### 9.3 Tooltip custom (warm)

```tsx
// frontend/src/components/charts/WarmTooltip.tsx
const WarmTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background:   chartTheme.tooltipBg,
      border:       `1px solid ${chartTheme.tooltipBorder}`,
      borderRadius: 12,
      padding:      "10px 14px",
      fontFamily:   "'Inter', sans-serif",
      boxShadow:    "0 4px 12px rgba(100,80,60,0.12)",
    }}>
      <p style={{ color: chartTheme.tooltipTextSecondary, fontSize: 11, margin: "0 0 4px" }}>
        {label}
      </p>
      {payload.map(entry => (
        <p key={entry.name} style={{
          color:      chartTheme.tooltipTextPrimary,
          fontSize:   16,
          fontWeight: 500,
          margin:     0,
          fontFamily: "'Space Grotesk', sans-serif",
        }}>
          {entry.value?.toLocaleString('es-AR')} kWh
        </p>
      ))}
    </div>
  );
};
```

### 9.4 Configuración de ejes y grid

```tsx
<CartesianGrid
  strokeDasharray={chartTheme.gridStrokeDash}
  stroke={chartTheme.gridStroke}
  vertical={false}
/>
<XAxis
  stroke="transparent"
  tick={{ fill: chartTheme.axisTickColor, fontSize: 11, fontFamily: "'Inter', sans-serif" }}
  tickLine={false}
  axisLine={false}
/>
<YAxis
  stroke="transparent"
  tick={{ fill: chartTheme.axisTickColor, fontSize: 11 }}
  tickLine={false}
  axisLine={false}
/>
```

---

## 10. Animaciones y transiciones

### 10.1 Motion Token System

**Archivo:** `docs/EPEC Design System/colors_and_type.css` — agregar al final:

```css
/* 🟢 MOTION TOKENS */
--motion-instant: 80ms;
--motion-fast:    150ms;
--motion-base:    250ms;
--motion-slow:    400ms;
--motion-xslow:   600ms;

--ease-out:    cubic-bezier(0.0, 0.0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

**Archivo:** `frontend/src/design-tokens.ts` — agregar al final:

```typescript
// 🟢 AGREGAR
export const motion = {
  duration: { instant: 80, fast: 150, base: 250, slow: 400, xslow: 600 },
  easing: {
    out:    "cubic-bezier(0.0, 0.0, 0.2, 1)",
    inOut:  "cubic-bezier(0.4, 0.0, 0.2, 1)",
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
  },
} as const;
```

### 10.2 Micro-animaciones

**Cards — hover lift sutil (Solora tiene hover states muy suaves):**

```css
.card-interactive {
  transition: transform 250ms ease-out, box-shadow 250ms ease-out;
  cursor: pointer;
}
.card-interactive:hover {
  transform: translateY(-1px);  /* muy sutil, no dramático */
  box-shadow: var(--shadow-md);
}
.card-interactive:active {
  transform: scale(0.995);
  transition-duration: 80ms;
}
```

**Counter animation en KPIs:** usar `react-countup` o implementación con `requestAnimationFrame`, duración 600ms ease-out, solo en el número hero de cada pantalla al montar.

**Progress bar:** `transition: width 600ms cubic-bezier(0.34, 1.56, 0.64, 1)` — spring para el fill.

**Chart bars:** `isAnimationActive={true}`, `animationDuration={600}`, `animationEasing="ease-out"` — Recharts defaults, no tocar.

**Page transitions:** fade suave de 350ms entre rutas.

---

## 11. Checklist de archivos a modificar

| Archivo | Tipo | Cambios | Prioridad |
|---|---|---|---|
| `docs/EPEC Design System/colors_and_type.css` | 🔴 Breaking rewrite | Neutral scale → warm, semantic tokens, superficies, shadows, radii, nuevos tokens | P0 |
| `frontend/src/design-tokens.ts` | 🔴 Breaking rewrite | `bg`, `fg`, `border`, `shadow`, `radius`, `font`, `cardStyle` + nuevos exports | P0 |
| `frontend/index.html` | 🔴 Breaking | Link Google Fonts → Inter + Space Grotesk | P0 |
| `frontend/src/components/AppShell.tsx` | 🔴 Breaking | Page bg warm, body bg warm | P1 |
| `frontend/src/pages/LoginPage.tsx` | 🔴 Breaking | Card radius 24px, bg warm-1, inputs warm | P1 |
| `frontend/src/pages/ObjetivosPage.tsx` | 🔴 Breaking | cardFeatured para proyección, progress warm, badge styles | P1 |
| `frontend/src/components/BloqueProyeccion.tsx` | 🔴 Breaking | cardFeaturedStyle, number hero size | P1 |
| `frontend/src/pages/HomePage.tsx` | 🔴 Breaking | Hero card → cardFeatured, bg warm, KWH hero typography | P1 (cuando exista) |
| `frontend/src/pages/ConsumoPage.tsx` | 🔴 Breaking | Chart warm theme, bars gradient | P1 (cuando exista) |
| `frontend/src/components/charts/` | 🟢 New | `ChartTheme.ts`, `WarmTooltip.tsx` | P1 |
| `frontend/src/components/Icon.tsx` | 🟢 New | Wrapper con strokeWidth 1.5 | P2 |
| `docs/EPEC Design System/README.md` | 🟢 Update | VISUAL FOUNDATIONS section | P2 |
| `docs/EPEC Design System/_ds_manifest.json` | 🟢 Update | Tokens actualizados | P2 |
| `docs/EPEC Design System/preview/*.html` | 🟢 Update | Todos los HTMLs de preview | P2 |
| `docs/stitch-prompts-plataforma-clientes.md` | 🔴 Breaking | Global Design Context + Apéndice A + prompts | P2 |

### 11.1 Comandos grep para auditar antes de migrar

```bash
# Usos de bg.surface, fg.primary etc. que cambian de valor
grep -r "bg\.surface\|fg\.primary\|fg\.secondary\|border\.default" frontend/src --include="*.tsx"

# Colores hardcoded que ya no son válidos
grep -rE "#f5f7f6|#ffffff|#111614|#4a5550|d5ddd9|1px solid" frontend/src --include="*.tsx"

# Cards con borde explícito a eliminar
grep -r "1px solid" frontend/src --include="*.tsx"
```

---

## 12. Migración del Global Design Context de Stitch

### 12.1 Nuevo Global Design Context completo

```text
GLOBAL DESIGN CONTEXT — EPEC Customer Platform (Warm Edition)

Product: responsive web app for residential electricity customers of EPEC, the state-owned
power utility of Córdoba, Argentina. Mobile viewport is the primary design reference.
Its purpose: help users understand, track and optimize their electricity consumption,
always expressed in kWh.

Visual theme: WARM LIGHT — inspired by Solora (Phenomenon Studio). Warm cream/sand
backgrounds, data-forward hierarchy, generous border radii. The aesthetic is organic,
precise and residential — not institutional.

Brand & visual style:
- Primary brand color: deep forest green #124e2f. Used as: top app bar, bottom nav bar,
  primary buttons, active nav indicators, progress bar fill, positive metric indicators.
  Light green tints #edf5f0 / #d4eedd for selected states.
- Page background: warm cream #F8F6F2 (NOT pure white, NOT neutral gray — a barely
  perceptible warm tint). Card surfaces: warm white #FDFCF9.
- Featured / highlighted cards: visible warm beige #F3EDE2 — used for the hero "Consumo"
  card, "Proyección" card, and any card that needs visual prominence. NO explicit border
  on these cards; the beige background itself creates separation. Border radius 20px.
- Standard cards: #FDFCF9 background, no border, shadow-sm, border radius 16px.
- Text: primary near-black warm #1C1410, secondary warm brown-gray #6B5A45, muted
  warm gray #8C7A63.
- Semantic colors: success #1d8348 (bg rgba(18,78,47,0.10)), warning #e6910a
  (bg rgba(230,145,10,0.10)), error #c0392b (bg rgba(192,57,43,0.08)),
  info #1565c0 (bg rgba(21,101,192,0.08)). Badge backgrounds are semi-transparent
  warm overlays — NOT solid light colors.
- Typography: Inter (variable font) for all UI text. Space Grotesk for kWh numbers,
  meter data, and numeric inputs — distinct, precise, technical.
- KWH numbers are the VISUAL HEROES: the largest elements in each card. The main kWh
  figure should be displayed at 40–48px in Space Grotesk weight 300, with the label
  ("Consumo acumulado del mes") small above or below it.
- No explicit borders on cards — surface contrast creates separation (warm-0 background
  vs warm-1 card vs warm-2 featured card).
- Corner radii: 4px tags/chips, 8px pills, 12px buttons/inputs, 16px cards, 20px
  featured cards and modals.
- Spacing: generous — card padding 32px standard, 40px featured. Section gaps 32–40px.
  Page padding 20px mobile, 40px desktop.
- Shadows: warm-tinted, subtle: rgba(100,80,60,0.08) not pure black.
- Icons: Lucide style, strokeWidth 1.5, 20px standard. Color inherits from text context.
- Motion: hover 150ms ease-out, transitions 250ms ease-in-out, chart entrance 600ms.
- Tone of copy: formal Argentine Spanish ("usted" register), sentence case, declarative,
  no exclamation marks. ALL UI text in Spanish exactly as written in the prompt.
- No photographic backgrounds, no illustrations, no emoji.

Non-negotiable product rules (unchanged):
1. kWh is the ONLY unit. Never show money, prices, $ or pesos anywhere.
2. Projections are always a RANGE (e.g. "198 – 226 kWh") with caption
   "Se ajusta a medida que avanza el mes".
3. Bad news always includes an actionable tip, phrased as opportunity.
4. Data latency always declared ("Datos disponibles hasta el 10/06/2026, 23:59").
5. Maximum granularity: DAILY. No hourly charts, no time-of-use bands.
6. No outage status, no claims/complaints, no subsidy blocks.
```

### 12.2 Apéndice A — Tokens para Stitch (reemplazar tabla)

```markdown
| Token | Valor |
|---|---|
| Tema global | Light warm cream |
| Primary / brand | `#124e2f` |
| Brand hover | `#1a6640` · pressed `#0f3d24` |
| Fondo de página | `#F8F6F2` (warm cream — no gris neutro) |
| Superficie card standard | `#FDFCF9` (warm white) |
| Superficie card featured | `#F3EDE2` (beige visible — card hero/proyección) |
| Selected/active bg | `#E8DFD0` |
| Separador warm | `#D4C4A8` |
| Texto primario | `#1C1410` (near-black cálido) |
| Texto secundario | `#6B5A45` (warm brown-gray) |
| Texto muted | `#8C7A63` |
| Borde cards | ninguno (contraste de superficie) |
| Borde inputs | `#D4C4A8` (1px warm) |
| Focus ring | `#1a6640` + sutil box-shadow |
| Success | `#1d8348` · bg `rgba(18,78,47,0.10)` |
| Warning | `#e6910a` · bg `rgba(230,145,10,0.10)` |
| Error | `#c0392b` · bg `rgba(192,57,43,0.08)` |
| Info | `#1565c0` · bg `rgba(21,101,192,0.08)` |
| Fuente UI | Inter variable (300–700) |
| Fuente técnica (kWh) | Space Grotesk (400 / 500) — hero number weight 300 |
| KWH hero size | 42–48px, weight 300, Space Grotesk |
| Radios | tags 4px · chips/pills 8px · buttons/inputs 12px · cards 16px · featured 20px |
| Sombra card | `0 1px 4px rgba(100,80,60,0.08)` |
| Sombra card featured | `0 8px 32px rgba(180,140,80,0.12)` |
| Espaciado card | 32px standard · 40px featured |
| Gap entre secciones | 32–40px |
| Iconos | Lucide strokeWidth 1.5, 20px |
```

### 12.3 Cambios clave por prompt de pantalla

| Pantalla | Cambios en el prompt |
|---|---|
| **4.1 Login** | Card sobre fondo `#F8F6F2`. Card bg `#FDFCF9`, radius 24px, sin borde, shadow-md warm. Button verde `#124e2f`. Inputs con border warm `#D4C4A8`. |
| **4.2 Onboarding** | Fondo `#F8F6F2`. Card sugerido: `#F3EDE2` (beige visible) radius 20px, no borde green — el beige comunica "destacado". Número grande `215 kWh` en Space Grotesk 300. |
| **4.3 Home normal** | Fondo `#F8F6F2`. Card "Consumo del mes": `#F3EDE2` (featured, radius 20px) — hero visual. `78 kWh` en 42px Space Grotesk 300. Cards secundarias: `#FDFCF9` radius 16px. Chips direction: warm semantic. |
| **4.4 Home empty** | Misma estructura warm. Empty states: bg `#F3EDE2`, texto `#8C7A63`, sin rojos. |
| **4.5 Consumo** | Barras verdes con gradiente `#227d50→#124e2f`. Barra anomalía amber `#c0780a`. Grid warm barely-visible. Alert card: borde izquierdo 3px amber. |
| **4.6 Drill-down** | Hero card `#F3EDE2`, `11,2 kWh` en 42px Space Grotesk. Chips `↑ 40%` en warning warm. |
| **4.7 Consumo desktop** | Sidebar `#124e2f` intocable. Content area `#F8F6F2`. Wide chart warm theme. |
| **4.8 Objetivos** | Card indicadores: `#FDFCF9`. Progress bar: warm track `#E8DFD0`, fill verde gradient/amber/rojo según estado. |
| **4.9 Mi Factura** | Cards `#FDFCF9`. Accordion hover: `rgba(18,78,47,0.06)`. Inputs con border warm. Info banner: borde izquierdo 3px `#1565c0`. |
| **4.10 Notificaciones** | Fondo `#F8F6F2`. Cards `#FDFCF9`. Unread dot: `#124e2f`. |
| **4.11 Config. notificaciones** | Cards `#FDFCF9`. Toggle off: track warm `#D4C4A8`. Toggle on: track verde. |
| **4.12 Configuración** | Avatar bg `#edf5f0` (green-50). Botón "Cerrar sesión": ghost danger. Chevrons `#8C7A63`. |

---

## 13. Plan de implementación sugerido

### 13.1 Fases

```
Fase 1 (tokens)       ──► Fase 2 (componentes)  ──► Fase 3 (páginas)  ──► Fase 4 (docs/stitch)
[1 día]                    [2 días]                   [2 días]              [1 día]
```

### 13.2 Fase 1 — Tokens (hacer todo junto, un commit)

1. `frontend/index.html` — actualizar Google Fonts import
2. `docs/EPEC Design System/colors_and_type.css` — reescribir tokens (sección 3 de este doc)
3. `frontend/src/design-tokens.ts` — reescribir exports (sección 3 de este doc)
4. Validar: `npx tsc --noEmit` en `/frontend` debe compilar
5. Validar visual: screenshot de `http://localhost:5173` → fondo debe ser warm cream, no gris

### 13.3 Fase 2 — Componentes (pueden ir en paralelo)

| Componente | Archivo | Cambio clave |
|---|---|---|
| AppShell / page wrapper | `AppShell.tsx` | Body bg → `#F8F6F2` |
| Cards base | todos los `.tsx` con `cardStyle` | Sin borde, radius 16px, padding 32px |
| Cards featured | `BloqueProyeccion.tsx` y similares | `cardFeaturedStyle`, bg `#F3EDE2`, radius 20px |
| Buttons | todos | Hover warm, radius 12px |
| Inputs | LoginPage, formularios | Border warm, focus verde |
| Badges/chips | Comparaciones, alertas | Warm badge backgrounds |
| Progress bar | `ObjetivosPage.tsx` | Track warm, fill gradient |
| Icon wrapper | nuevo `Icon.tsx` | strokeWidth 1.5 |

**Validación de Fase 2:**
- Verificar contraste WCAG AA: texto `#1C1410` sobre `#F3EDE2` → ratio ≥ 4.5:1 ✓
- Verificar contraste WCAG AA: texto `#6B5A45` sobre `#FDFCF9` → ratio ≥ 4.5:1 ✓

### 13.4 Fase 3 — Páginas

| Página | Prioridad | Foco |
|---|---|---|
| LoginPage | P1 | Primera impresión; hero card `#F3EDE2` radius 24px |
| AppShell (nav) | P1 | Sidebar mantiene verde; page bg warm |
| BloqueProyeccion | P1 | Featured card beige, número range prominente |
| ObjetivosPage | P1 | Indicadores, progress bar, número objetivo hero |
| HomePage | P1 (cuando exista) | Hero "78 kWh" en 42px Space Grotesk |
| ConsumoPage | P2 (cuando exista) | Chart warm theme |

**Validación Fase 3 — por cada página:**

```bash
# Dev server debe estar corriendo
agent-browser open http://localhost:5173/<ruta>
agent-browser wait --load networkidle
agent-browser screenshot <pantalla>-warm.png
# Luego Read() el screenshot y verificar:
```

Checklist visual por pantalla:
- [ ] Fondo de página es warm cream (no blanco puro, no gris)
- [ ] Cards visibles sin bordes explícitos (excepto inputs)
- [ ] Card hero/featured con fondo beige `#F3EDE2` notoriamente diferente al fondo de página
- [ ] Número kWh principal es el elemento más grande visualmente (≥ 36px)
- [ ] Border radius generosos (mínimo 12px en interactivos, 16px en cards)
- [ ] Verde EPEC solo en sidebar, top bar, CTAs, activos, positivos
- [ ] Sombras sutiles y warm (sin negro puro)
- [ ] Sin bordes 1px en cards de dashboard

### 13.5 Fase 4 — Docs y Stitch

1. Actualizar `docs/stitch-prompts-plataforma-clientes.md` — sección 2 y Apéndice A (ver sección 12)
2. Actualizar cada prompt individual (sección 12.3)
3. Actualizar `docs/EPEC Design System/README.md`
4. Actualizar `docs/EPEC Design System/_ds_manifest.json`

---

*Fin del documento — versión 2.0 · 2026-06-19 · Verificado contra Dribbble shot #27210300 con agent-browser*
