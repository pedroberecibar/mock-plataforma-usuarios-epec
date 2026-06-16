# Skill: session-bootstrap

**Alias de invocación:** `/start-session`

## Propósito
Cargar el contexto completo del proyecto al inicio de cada sesión de trabajo, para que Claude retome exactamente donde quedó sin necesidad de explicaciones manuales.

## Qué hace al invocar `/start-session`

1. **Lee `CLAUDE.md`** — reglas permanentes del proyecto (stack, TDD, arquitectura, seguridad, git).
2. **Lee `MEMORY.md`** — conocimiento arquitectónico acumulado (decisiones, patrones, anti-patrones).
3. **Lee `CONTEXT.md`** — estado de la última sesión (qué se completó, qué quedó pendiente, primer paso sugerido).
4. **Corre `git status`** — muestra archivos modificados, en staging y untracked.
5. **Corre `git log --oneline -10`** — últimos 10 commits para orientarse.
6. **Resume en una frase** el estado actual del proyecto.
7. **Propone el primer paso** concreto para esta sesión, basado en lo que quedó pendiente en CONTEXT.md.

## Instrucciones para Claude

Al recibir `/start-session`:

```
1. Leer los tres archivos de continuidad (CLAUDE.md, MEMORY.md, CONTEXT.md).
2. Ejecutar: git status
3. Ejecutar: git log --oneline -10
4. Responder con este formato:

---
## Estado al inicio de sesión — [fecha]

**Resumen en una frase:** [Estado actual del proyecto]

**Último trabajo:** [Qué se completó en la sesión anterior]

**Pendiente:** [Qué quedó sin terminar]

**Tests fallando intencionalmente:** [Listar o "Ninguno"]

**Primer paso sugerido:** [Acción concreta y específica]

**Git status:**
[output de git status]
---
```

## Notas
- Si `CONTEXT.md` está vacío o es el primer arranque, decirlo explícitamente y pedir al usuario que describa el estado actual.
- Si hay tests fallando intencionalmente (RED del ciclo TDD), nombrarlos; es normal y esperado.
- No asumir que el estado es "limpio" si git status muestra cambios sin commitear.
