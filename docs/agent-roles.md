# Roles y uso de agentes

Referencia rápida: cuándo invocar cada agente y qué esperar de él.

## Resumen

| Agente | Cuándo | Input | Output |
|--------|--------|-------|--------|
| `code-reviewer` | Antes de todo merge | Diff del PR o rama | Hallazgos por severidad + veredicto |
| `security-reviewer` | Antes de merge si toca auth/SQL/archivos | Código a revisar | Hallazgos OWASP/STRIDE + veredicto |
| `ui-designer` | Al arrancar cualquier componente de UI | Brief del proyecto | Token system + componente de referencia |
| `docs-updater` | Al cerrar una tarea significativa | — (usa git diff) | Archivos actualizados + nota al vault |

---

## `code-reviewer`

**Propósito:** Revisor crítico de PRs. No aprueba por default.

**Cuándo invocar:**
- Antes de hacer merge de cualquier rama a `main`.
- Antes de compartir código con otro equipo.
- Cuando querés un segundo ojo sobre una decisión de diseño.

**Qué analiza:**
- Blast radius (qué puede romperse, via Serena).
- Corrección, diseño, seguridad básica, mantenibilidad.
- Calidad de tests (¿son reales? ¿cubren edge cases?).

**Cómo invocar:**
```
claude --agent code-reviewer
"Revisá el PR de esta rama: [describe los cambios]"
```

---

## `security-reviewer`

**Propósito:** Mentalidad adversarial. OWASP Top 10 + STRIDE.

**Cuándo invocar (obligatorio):**
- Cambios en autenticación o autorización.
- Queries SQL nuevas o modificadas.
- Manejo de archivos (upload, lectura, paths).
- Endpoints públicos nuevos.
- Cualquier integración con sistema externo.

**Output:** Hallazgos por severidad (CRÍTICO / ALTO / MEDIO / BAJO / INFORMATIVO). Si no hay hallazgos, dice "CLEAN" con justificación.

**Cómo invocar:**
```
claude --agent security-reviewer
"Revisá la seguridad del módulo de autenticación en src/infrastructure/auth/"
```

---

## `ui-designer`

**Propósito:** Identidad visual única. Prohíbe el "Claude default look".

**Cuándo invocar:**
- Al arrancar cualquier proyecto con componentes de UI.
- Antes de codear el primer componente.
- Cuando el diseño se ve genérico y no representa el proyecto.

**Proceso:**
1. Brief del proyecto (tipo de app, usuario, restricciones).
2. Token system (colores, tipografía, espaciado, radio).
3. Componente de referencia (botón + card + input).
4. Auto-crítica (checklist de no-genericidad).

**Cómo invocar:**
```
claude --agent ui-designer
"Definí la identidad visual para el dashboard de auditoría de EPEC"
```

---

## `docs-updater`

**Propósito:** Mantener ADRs, MEMORY.md y el vault al día con el código real.

**Cuándo invocar:**
- Al cerrar una tarea significativa.
- Cuando se toma una decisión técnica que debería quedar registrada.
- Automáticamente via hook PostToolUse (si está configurado).

**Cómo invocar:**
```
claude --agent docs-updater
"Actualizá la documentación con los cambios de la sesión de hoy"
```

---

## Principios de uso

1. **Un agente = una tarea.** No pedirle a `code-reviewer` que también actualice la doc.
2. **Modelo distinto al autor.** Para evitar loop de complacencia, el reviewer debería ser un modelo diferente al que escribió el código. Cambiá el modelo antes de invocar el agente reviewer.
3. **No saltear el reviewer.** "Es un cambio chico" no es excusa. Los bugs más caros vienen de los "cambios chicos".
4. **Los agentes son exigentes.** Si `security-reviewer` dice "CLEAN", confiar. Si dice "CRÍTICO", no hacer merge hasta resolver.
