# Manual de Subagentes Especializados

Este documento describe los agentes disponibles en `.claude/agents/`, cuándo invocarlos y qué esperar de cada uno.

## Agentes disponibles

### `code-reviewer`
**Cuándo:** Al abrir un PR o antes de mergear cualquier rama.
**Qué hace:** Revisa el código con mentalidad crítica. Analiza blast radius (qué puede romper el cambio) usando Serena. No aprueba por default.
**Output:** Lista estructurada de hallazgos con severidad y sugerencia concreta.
**Cómo invocar:** `claude --agent code-reviewer`

---

### `security-reviewer`
**Cuándo:** Antes de todo merge a `main`. Obligatorio si se toca autenticación, queries SQL, manejo de archivos o endpoints públicos.
**Qué hace:** Mentalidad adversarial. OWASP Top 10 + STRIDE. Detecta SQL injection, secrets hardcodeados, path traversal, etc.
**Output:** Hallazgos por severidad: CRÍTICO / ALTO / MEDIO / BAJO / INFORMATIVO. Si está limpio, dice "CLEAN" con justificación.
**Cómo invocar:** `claude --agent security-reviewer`

---

### `ui-designer`
**Cuándo:** Al arrancar cualquier componente de UI nuevo. No codear frontend sin pasar por este agente primero.
**Qué hace:** Define identidad visual única por proyecto. Token system (colores, tipografías, espaciado) antes de código. Prohíbe el "Claude default look".
**Output:** Documento de tokens + decisiones de diseño + primer componente de referencia.
**Cómo invocar:** `claude --agent ui-designer`

---

### `docs-updater`
**Cuándo:** Al cerrar una tarea significativa o cuando se toca un archivo de dominio. También se puede disparar por hook PostToolUse.
**Qué hace:** Actualiza ADRs relevantes, sincroniza el vault de Obsidian con las decisiones tomadas, revisa si el README sigue vigente.
**Output:** Lista de archivos actualizados + nota de cambios.
**Cómo invocar:** `claude --agent docs-updater`

---

## Principio de uso

Un agente = una tarea = una rama = un worktree (cuando aplica trabajo paralelo). No mezclar roles en una sola invocación. El reviewer es idealmente un **modelo distinto** al que escribió el código, para evitar loop de complacencia.
