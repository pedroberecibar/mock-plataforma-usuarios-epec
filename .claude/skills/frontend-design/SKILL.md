# Skill: frontend-design

## Propósito
Garantizar identidad visual única y coherente en cada proyecto. Prohíbe el "Claude default look" (gradiente morado, Inter como única fuente, sombras genéricas). Obliga a definir un **token system** antes de escribir cualquier código de UI.

## Regla de oro

> **Ningún componente se escribe sin un token system aprobado.**

Si el usuario pide "hacé el formulario de login", la respuesta correcta es primero: "¿Cuál es la identidad visual del proyecto?", no generar código.

---

## Paso 1 — Definir el token system (obligatorio)

Antes de cualquier código, documentar:

### Colores (4–6 colores nombrados con su rol)
```
--color-primary:    #[hex]    /* Acción principal, CTAs */
--color-secondary:  #[hex]    /* Acción secundaria, links */
--color-surface:    #[hex]    /* Fondo de cards, modales */
--color-background: #[hex]    /* Fondo de página */
--color-text:       #[hex]    /* Texto principal */
--color-text-muted: #[hex]    /* Texto secundario, placeholders */
--color-danger:     #[hex]    /* Errores, destructive actions */
--color-success:    #[hex]    /* Confirmaciones, estados OK */
```

**Criterios:**
- No usar colores nombrados de CSS (`red`, `blue`). Siempre hex o HSL curado.
- Verificar contraste mínimo WCAG AA: 4.5:1 para texto normal, 3:1 para texto grande.
- El color primario debe distinguir este proyecto de cualquier otro.

### Tipografía (2–3 fuentes con roles)
```
--font-heading: '[Nombre]', [fallback]  /* Títulos, H1-H3 */
--font-body:    '[Nombre]', [fallback]  /* Cuerpo, párrafos, labels */
--font-mono:    '[Nombre]', monospace   /* Código, IDs técnicos */
```

**Criterios:**
- No usar Inter como única fuente sin justificación.
- Elegir de Google Fonts si el proyecto es interno (offline-capable si aplica).
- Documentar por qué esa fuente y no otra.

### Espaciado y radio
```
--space-xs:  4px
--space-sm:  8px
--space-md:  16px
--space-lg:  24px
--space-xl:  40px

--radius-sm: 4px
--radius-md: 8px
--radius-lg: 16px
--radius-full: 9999px
```

### Sombras y elevación
```
--shadow-card:   0 2px 8px rgba(0,0,0,0.08)
--shadow-modal:  0 8px 32px rgba(0,0,0,0.16)
--shadow-focus:  0 0 0 3px [color-primary con 30% opacidad]
```

---

## Paso 2 — Definir la "voz visual" del proyecto

Responder en una oración para cada dimensión:

| Dimensión | Pregunta | Ejemplo |
|-----------|----------|---------|
| **Tono** | ¿Serio/corporativo o amigable/moderno? | "Serio con detalles de precisión técnica" |
| **Densidad** | ¿Mucha información o espacio generoso? | "Alta densidad, es una herramienta de auditoría" |
| **Diferenciador** | ¿Qué hace que NO parezca cualquier dashboard? | "Paleta de azules EPEC con acentos naranjas de alerta" |

---

## Paso 3 — Componente de referencia

Crear UN componente de referencia antes de los demás (generalmente la card o el botón primario). Todos los demás componentes deben ser consistentes con ese primero.

---

## Anti-patrones prohibidos

| ❌ Prohibido | ✅ Alternativa |
|------------|--------------|
| Gradiente morado sin justificación | Gradiente derivado del color primario del proyecto |
| Solo Inter como tipografía | Combinar con fuente de display para headings |
| Sombras genéricas `box-shadow: 0 4px 6px rgba(0,0,0,0.1)` | Sombras calibradas a la paleta y elevación |
| Colores `#3b82f6` (Tailwind blue-500) sin variación | Curar el color específico para el proyecto |
| Cards sin personalidad (borde fino gris, fondo blanco) | Usar surface color del token system |
| Botones con `border-radius: 4px` siempre | Decidir el radio según la "personalidad" del proyecto |

---

## Auto-crítica final (antes de entregar)

Antes de dar por terminado cualquier diseño, responder:

1. **¿Se confunde este diseño con el output por defecto de Claude?** Si la respuesta es "quizás sí" → revisar color primario y tipografía.
2. **¿Podría ser el dashboard de cualquier SaaS genérico?** Si sí → agregar el elemento diferenciador.
3. **¿Los colores son accesibles?** Verificar contraste con herramienta (ej: WebAIM Contrast Checker).
4. **¿El hover/focus/active state es visible?** Todo elemento interactivo debe tener estado visual explícito.
5. **¿Los estados de error/éxito/loading están diseñados?** No solo el happy path.

---

## Referencia de fuentes recomendadas (Google Fonts, offline-capable)

| Uso | Candidatos |
|-----|-----------|
| Heading impactante | Sora, Space Grotesk, DM Sans, Lexend |
| Body legible en densidad alta | Inter, Geist, IBM Plex Sans, Nunito Sans |
| Mono para datos técnicos | JetBrains Mono, Fira Code, IBM Plex Mono |
| Combo corporativo serio | Outfit (heading) + Inter (body) |
| Combo moderno amigable | Plus Jakarta Sans (heading) + Nunito (body) |
