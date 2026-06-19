# Sprint Handoff Protocol

> Proceso estándar que cada agente ejecuta al terminar su sprint, cuando el
> usuario lo solicita ("handoff", "prepará el próximo agente", "dejá listo
> para el próximo sprint" o similar). Genera el prompt del próximo agente y
> actualiza `CONTEXT.md`.

---

## Pasos del handoff

### 1. Capturar estado del repo

```bash
git status
git log --oneline -8
```

Identificar:
- Último sprint committeado.
- Cambios sin commitear (describirlos brevemente; recordar al usuario hacer commit
  si corresponde antes de pasar el control).

---

### 2. Validar implementación vs Notion MVP

Hacer fetch de la página de producto en Notion:

```
mcp__claude_ai_Notion__notion-fetch  id="37b62e87-5521-8001-ac13-d418201ab1aa"
```

> **Fallback si Notion no está disponible:** usar los CU definidos en
> `docs/PLAN-SPRINTS-MVP.md` como fuente de verdad y marcar la validación
> como "basada en doc local (Notion no disponible)".

Producir una tabla de brechas con este formato:

```
| CU      | Descripción                          | Estado | Notas                  |
|---------|--------------------------------------|--------|------------------------|
| CU-H01  | Consumo del mes + deltas             | ✅     |                        |
| CU-C06  | Consumo anómalo                      | ❌     | Sprint 10              |
| CU-A01  | Push notifications                   | ⚠️     | Solo email, sin web push |
```

Estados: ✅ implementado · ❌ pendiente · ⚠️ parcial/deuda técnica.

---

### 3. Identificar el próximo sprint

Leer `docs/PLAN-SPRINTS-MVP.md` y determinar cuál es el siguiente sprint no
completado. Confirmar con el usuario si hay ambigüedad.

---

### 4. Actualizar `CONTEXT.md`

Sobreescribir con el template estándar (mismo que el auto-cierre del CLAUDE.md):

```markdown
# Estado de Sesión Actual

## Última sesión
- **Fecha:** YYYY-MM-DD
- **Qué se completó:** [archivos y funciones concretas con nombres exactos]
- **Qué quedó incompleto:** [tarea + bloqueante si aplica, o "—"]
- **Decisiones técnicas no documentadas:** [o "—"]
- **Primer paso para la próxima sesión:** Sprint N — [descripción concreta]
- **Tests fallando intencionalmente:** [lista o "Ninguno"]

## Estado del repo
[output de git status y git log --oneline -5]
```

---

### 5. Generar el prompt del próximo agente

Usar el template de abajo. El prompt debe ser **auto-contenido**: el agente
receptor no leerá esta conversación, no tendrá memoria del contexto previo.

---

## Template del prompt para el agente siguiente

```
Sos un agente de desarrollo full-stack trabajando en la **Plataforma de
Clientes EPEC** (MVP). Tu misión es implementar el **Sprint [N] — [Nombre]**
de acuerdo al plan en `docs/PLAN-SPRINTS-MVP.md`.

---

## Lo primero que tenés que hacer

1. Leer `CLAUDE.md` completo — contiene las reglas del proyecto (TDD, Ports &
   Adapters, idioma, UI, validación en browser).
2. Leer `CONTEXT.md` — estado real del repo al inicio de tu sprint.
3. Ejecutar `git status` y `git log --oneline -5` para confirmar el punto de
   partida.
4. Leer `docs/PLAN-SPRINTS-MVP.md` — plan completo de sprints con el DoD de
   tu sprint.

---

## Stack

- **Backend:** Python 3.12 + FastAPI · SQLite (aiosqlite + SQLAlchemy async)
- **Frontend:** React + TypeScript + Vite
- **Tests:** pytest (backend) · Vitest + React Testing Library (frontend)
- **Arquitectura:** Ports & Adapters. `domain` → `application` → `infrastructure`.
  Ningún caso de uso importa una lib de infra directa.
- **TDD obligatorio:** RED → GREEN → REFACTOR. Test falla antes de implementar.
- **Idioma:** código en inglés · UI y lógica de negocio en español rioplatense.

---

## Estado actual (sprint [N-1] completado)

[RESUMEN DE LO YA IMPLEMENTADO — qué existe, qué no tocar]

Commits recientes:
- [hash] feat(sprint-[N-1]): ...
- [hash] feat(sprint-[N-2]): ...

Tests al inicio: [X] backend · [Y] frontend.
Tests fallando intencionalmente: [lista o "Ninguno"].
Cambios sin commitear: [lista o "Ninguno"].

---

## Tu trabajo en este sprint

[DESCRIPCIÓN DETALLADA DEL SPRINT — CU a implementar, historias, subtareas
backend y frontend, dependencias a resolver primero]

---

## Criterios de Done

- [ ] pytest verde (incluyendo tests nuevos por capa: use case con fakes,
      router, SQLite si aplica)
- [ ] mypy sin errores nuevos
- [ ] ruff sin errores nuevos
- [ ] vitest verde (tests para cada nuevo componente / página)
- [ ] tsc --noEmit verde
- [ ] [criterios funcionales específicos del sprint]
- [ ] Validación visual en browser (agent-browser o documentar si no disponible)

Conventional Commit al cerrar:
`feat(sprint-[N]): [descripción corta]`

---

## Al terminar tu sprint

Cuando el usuario te diga "handoff", "prepará el próximo agente" o similar,
seguí el protocolo definido en `docs/SPRINT-HANDOFF-PROTOCOL.md`:
1. git status + git log
2. Validar vs Notion (ID: 37b62e87-5521-8001-ac13-d418201ab1aa) o vs
   `docs/PLAN-SPRINTS-MVP.md` si Notion no está disponible
3. Producir tabla de brechas (✅ / ❌ / ⚠️)
4. Actualizar CONTEXT.md
5. Generar prompt del próximo agente usando este mismo template
```

---

## Notas de mantenimiento

- **ID Notion de la página de producto:** `37b62e87-5521-8001-ac13-d418201ab1aa`
- **Plan de sprints local:** `docs/PLAN-SPRINTS-MVP.md`
- Actualizar este archivo si el template cambia o si se agrega un nuevo canal
  de referencia (nueva página Notion, nuevo ADR, etc.).
