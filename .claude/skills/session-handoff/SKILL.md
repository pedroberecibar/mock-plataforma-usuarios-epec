# Skill: session-handoff

**Alias de invocación:** `/end-session`

## Propósito
Cerrar la sesión de trabajo documentando el estado exacto para que la próxima sesión (o un agente distinto) pueda retomar sin fricción. Elimina el "¿dónde estaba?" al reiniciar.

## Qué hace al invocar `/end-session`

Actualiza `CONTEXT.md` con exactamente:
1. **Qué se completó** — archivos concretos creados/modificados y funciones/clases afectadas.
2. **Qué quedó incompleto y por qué** — tarea en curso, bloqueante si lo hay.
3. **Decisiones técnicas tomadas** no documentadas aún en MEMORY.md.
4. **Qué hacer primero la próxima sesión** — paso concreto y accionable.
5. **Tests fallando intencionalmente** — fase RED del ciclo TDD (listar nombre del test y por qué falla).

Luego hace **append** de una nota al vault de Obsidian (`${VAULT_PATH}/Projects/`) con un resumen del día.

## Instrucciones para Claude

Al recibir `/end-session`:

```
1. Generar un resumen de la sesión respondiendo las 5 preguntas arriba.
2. Sobreescribir CONTEXT.md con ese resumen usando este template:

---
# Estado de Sesión Actual

## Última sesión
- **Fecha:** [YYYY-MM-DD]
- **Qué se completó:** [archivos y funciones concretas]
- **Qué quedó incompleto:** [tarea + bloqueante si aplica]
- **Decisiones técnicas no documentadas:** [o "—"]
- **Primer paso para la próxima sesión:** [acción concreta]
- **Tests fallando intencionalmente:** [lista o "Ninguno"]

## Estado del repo
[output de git status y git log --oneline -5]
---

3. Si VAULT_PATH está configurado en .env, append al vault:
   Archivo: ${VAULT_PATH}/Projects/[nombre-proyecto]-[YYYY-MM-DD].md
   Contenido: resumen de la sesión en formato legible.

4. Recordar al usuario hacer commit si hay cambios sin commitear.
```

## Notas
- La nota al vault es opcional si VAULT_PATH no está configurado; avisar pero no fallar.
- Si hay decisiones técnicas importantes, preguntar si agregarlas a MEMORY.md antes de cerrar.
- Si quedan tests en RED intencionalmente, documentarlos explícitamente para no confundir en la próxima sesión.
