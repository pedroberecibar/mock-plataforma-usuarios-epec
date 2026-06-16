# EPEC Design System

**EPEC — Empresa Provincial de Energía de Córdoba**
Provincial electricity utility serving Córdoba, Argentina.

## Company & Product Context

EPEC is the state-owned electric power company of Córdoba Province, Argentina. It handles generation, transmission, and distribution of electricity across the province, serving residential, commercial, and industrial customers.

### Products / Surfaces Identified

1. **Internal Commercial Management System** — A desktop web application used by EPEC's *Gerencia Comercial* (Commercial Management) for billing, meter reading, contract management, and customer supply records. Key workflows include: supply identification, distributed generation (GD) configuration, OBIS code registration, meter reading, and invoice generation.

2. **Customer-Facing Documentation / PDF Reports** — Formal internal training documents and technical guides (e.g., "Suministros con Generación Distribuida") distributed as PDF presentations.

### Distributed Generation Context

EPEC has introduced support for **Generación Distribuida (GD)** — customers with their own renewable energy sources (solar, wind) who can inject surplus energy back into the grid. This requires:
- Bidirectional metering (import + export)
- Time-of-use discrimination: **Resto** (05:00–18:00), **Pico** (18:00–23:00), **Valle** (23:00–05:00)
- 7-register OBIS codes: EAR, EAP, EAV, IER, IEP, IEV, ERT
- Special billing tab in the commercial system: *"E. Distribuida"*

### Sources Provided

- `uploads/SUMINISTROS CON GENERACION DISTRIBUIDA - NICO 1.pdf` — 10-page internal training deck, Gerencia Comercial
- `uploads/epe.png` — EPEC primary logo (dark green square, white "E")
- `uploads/image 2 (2).png` — EPEC logo, reversed/white version on dark background

---

## CONTENT FUNDAMENTALS

**Language:** Spanish (Argentine). All UI copy and documentation is in Spanish.

**Tone:** Institutional, technical, and formal. EPEC communicates as a government utility — authoritative, clear, and precise. No casual language, no marketing hyperbole.

**Voice:**
- Third-person or impersonal constructions preferred: *"El suministro toma energía…"*, *"Se registran los siguientes cuadrantes…"*
- Instructional copy uses numbered steps and bullet points
- Direct addresses use *usted* (formal) rather than *vos/tú*
- No emoji used anywhere in communications or UI
- No exclamation marks; neutral declarative sentences

**Casing:**
- Section headers: ALL CAPS (e.g. *"¿QUÉ ES UN SUMINISTRO CON GENERACIÓN DISTRIBUIDA?"*)
- UI labels: Title Case in Spanish
- Body text: sentence case

**Specific examples:**
> *"Un suministro con generación distribuida es aquel que, además de consumir energía eléctrica de la red, cuenta con una fuente de generación propia…"*
> *"Este método es el más certero y abarca todos los grupos tarifarios."*
> *"Identificación, medición, lecturas y facturación"*

---

## VISUAL FOUNDATIONS

### Colors
- **Primary Green:** `#124e2f` — deep forest green; used as the primary brand/logo background, key UI accents, and header elements.
- **White:** `#FFFFFF` — primary text on dark backgrounds; clean backgrounds.
- **Light Green Tints:** Derived from the primary for hover states, backgrounds, subtle fills.
- **Neutral Grays:** Standard system of light/mid/dark grays for UI scaffolding.
- **Semantic:** Error red, warning amber, success green (all derived from utility conventions).

### Typography
- **Display/Heading:** **Roboto** — confirmed from inspection of EPEC's official website (`font-family: Roboto, sans-serif`). Loaded from Google Fonts.
- **Body/UI:** Roboto Regular/Medium; tight line-height for dense data tables.
- **Mono:** Used for OBIS codes, tariff codes, supply numbers — `JetBrains Mono`.
- Sizes: Large header 28–32px, section heads 18–22px, body 14–16px, labels/captions 12px.

### Backgrounds & Surfaces
- White backgrounds dominate for content areas
- Dark green (`#124e2f`) used for headers, sidebars, hero banners, and modal headers
- Light green tint backgrounds (`#edf5f0`) for highlighted sections, info cards
- No photographic backgrounds; no gradients in main UI
- PDF documents use white with dark green accents

### Spacing & Layout
- Dense, data-heavy layouts (utility billing system)
- Fixed left sidebar navigation pattern
- 4px base grid; standard spacing scale: 4, 8, 12, 16, 24, 32, 48px
- Tables are the primary data component — bordered, compact, striped

### Cards & Containers
- Thin 1px borders (`#d0d7d3` approx.) on cards and containers
- Minimal border-radius: 2–4px (institutional, not playful)
- Light shadow: `0 1px 3px rgba(0,0,0,0.08)` — very subtle
- No colored left-border accent cards

### Iconography
- See ICONOGRAPHY section below — primarily Lucide icons via CDN

### Animation & Interaction
- Minimal animation; this is a utility management system
- Hover states: background color lightens slightly; no scale transforms
- Press states: slight darkening of background
- No bounce or springy transitions; utility-appropriate

### Corner Radii
- `2px` — table cells, tags, small badges
- `4px` — buttons, inputs, cards
- `6px` — modals, panels

### Imagery
- No decorative photography
- Technical diagrams and flow charts in documentation
- Logo on dark green backgrounds for official materials

---

## ICONOGRAPHY

**Approach:** EPEC uses clean, functional iconography appropriate for a utility management system. No custom icon font identified in provided materials.

**Substitution:** Using **Lucide Icons** (CDN: `https://unpkg.com/lucide@latest/dist/umd/lucide.min.js`) — thin stroke, 24px grid, consistent weight. Flag: this is a substitute; confirm with EPEC's actual system.

**No emoji** used in any EPEC materials.

**Key icons in use:**
- Electricity / lightning bolt: `zap`
- Meter reading: `gauge`
- Solar/generation: `sun`
- Export/injection: `arrow-up-right`
- Import/consumption: `arrow-down-left`
- Settings / configuration: `settings`
- Calendar / date: `calendar`
- User / customer: `user`
- Contract / document: `file-text`
- Invoice / billing: `receipt`

Logos: `assets/epec-logo-primary.png` (★ primary: icon + wordmark), `assets/epec-logo-green.png` (icon only, green bg), `assets/epec-logo-white.png` (white reversed version)

---

## FILE INDEX

```
README.md                    ← This file; full design system documentation
SKILL.md                     ← Agent skill descriptor
colors_and_type.css          ← All CSS custom properties (colors, type, spacing)
assets/
  epec-logo-green.png        ← Primary logo (green bg, white E)
  epec-logo-white.png        ← Reversed logo (white, for dark backgrounds)
preview/
  colors-primary.html        ← Primary green scale
  colors-neutral.html        ← Neutral gray scale
  colors-semantic.html       ← Semantic colors (status)
  type-scale.html            ← Typography scale specimens
  type-mono.html             ← Monospace / code specimens
  spacing-tokens.html        ← Spacing scale tokens
  shadows-radii.html         ← Shadow system & border radii
  btn-components.html        ← Button states
  form-inputs.html           ← Input fields, selects
  badges-tags.html           ← Status badges, tags
  tables.html                ← Data table component
  logo-usage.html            ← Logo usage guidelines
ui_kits/
  commercial/
    README.md                ← UI kit overview
    index.html               ← Interactive commercial portal prototype
    Sidebar.jsx              ← Navigation sidebar
    TopBar.jsx               ← Top header bar
    SupplyTable.jsx          ← Supply list data table
    SupplyDetail.jsx         ← Supply detail / GD configuration screen
    BillingPanel.jsx         ← Billing / invoice panel
```
