# Reglas del proyecto para Claude Code

## ⚡ Auto-bootstrap (ejecutar SIEMPRE al iniciar una sesión nueva)

Al comenzar **cualquier conversación nueva**, antes de responder cualquier cosa:

1. Leer `MEMORY.md` — conocimiento arquitectónico acumulado del proyecto.
2. Leer `CONTEXT.md` — estado de la última sesión (qué quedó pendiente, qué hacer primero).
3. Ejecutar: `git status`
4. Ejecutar: `git log --oneline -5`
5. Responder con este formato exacto:

```
## Sesión iniciada — [fecha]
**Estado:** [una frase sobre el proyecto]
**Último trabajo:** [qué se completó]
**Pendiente:** [qué quedó sin terminar]
**Primer paso sugerido:** [acción concreta]
```

Si `CONTEXT.md` no tiene sesión previa, decirlo y pedir al usuario que describa el estado.

## ⚡ Auto-cierre (ejecutar SIEMPRE cuando el usuario indica que termina)

Cuando el usuario dice `/end-session`, "terminamos", "cerramos" o similar:

1. Generar resumen de la sesión.
2. Sobreescribir `CONTEXT.md` con el template:

```
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
```

3. Si `VAULT_PATH` está en `.env`, hacer append al vault con la nota del día.
4. Recordar hacer commit si hay cambios sin commitear.

---

## Stack del proyecto

Proyecto: **Plataforma de Clientes EPEC** (MVP).

- **Backend:**  Python 3.12+ + FastAPI
- **Frontend:** React + TypeScript (Vite)
- **Tests:**    pytest (backend) · Vitest + React Testing Library (frontend)
- **DB:**       SQLite (ver ADR-001)
- **Otros:**    EPEC Design System (ver `docs/EPEC Design System/`), prompts de Stitch para UI (`docs/stitch-prompts-plataforma-clientes.md`)

## Idioma
- Código, nombres y comentarios técnicos: inglés
- Lógica de negocio, ADRs, contenido operativo: español rioplatense

## TDD Protocol (OBLIGATORIO — independiente del stack)
1. RED: escribí un test que falle. Corrélo. Confirmá que falla. NO escribas implementación todavía.
2. GREEN: escribí la implementación MÍNIMA que pasa el test. Nada más.
3. REFACTOR: mejorá calidad. Todos los tests siguen en verde tras cada cambio.
4. NUNCA escribas tests que reflejen la lógica de implementación. Los tests definen comportamiento.
5. NUNCA generes tests después para satisfacer métricas de cobertura.

## Architecture Rules (independiente del stack — enforced by CI)
- Single Responsibility: una razón para cambiar por clase/función. Archivo > 300 líneas → flag para extracción.
- Open/Closed: extendé con clases/funciones nuevas, no modificando existentes. Cambiar de tecnología externa (SQLite→Postgres, proveedor de cola/notificaciones/auth/fuente de datos) = agregar un adapter nuevo en infrastructure, NUNCA tocar casos de uso. Ver ADR-001.
- Dependency Inversion: dependé de abstracciones. La capa domain NO importa infraestructura. application/domain definen los puertos (clases abstractas `abc.ABC`); infrastructure provee los adapters concretos. Ningún caso de uso importa una lib de infra concreta (sqlite3/SQLAlchemy, cliente Oracle, Redis/Celery, push/email, JWT) — siempre a través de su puerto. Puertos del proyecto: `ConsumoDiarioRepository`, `ObjetivoConsumoRepository`, `VecinosRepository`, `MedicionSourceReader` (Oracle), `TaskQueue`, `NotificationSender`, `AuthProvider`.
- DRY: nada de bloques duplicados > 5 líneas.
- YAGNI: implementá solo lo necesario AHORA. Sin generalización especulativa.

## Seguridad (independiente del stack)
- NUNCA hardcodear secrets. NUNCA incluir credenciales en este archivo.
- Queries a BD siempre parametrizadas, nunca concatenadas.
- Input del usuario siempre validado antes de usarse.

## Git
- Conventional Commits. GitHub Flow. Worktrees para trabajo paralelo.
- Máximo 2-3 worktrees activos en paralelo (restricción de RAM en entornos modestos).

## UI / Diseño (OBLIGATORIO para cualquier componente frontend)

**Fuente de verdad visual: proyecto Stitch "EPEC Plataforma Clientes — Desktop".**

- Toda pantalla o componente nuevo **debe ajustarse al diseño aprobado en Stitch** (proyecto accesible vía MCP `mcp__stitch__*`).
- Antes de codear cualquier componente de UI: consultá el proyecto Stitch (`mcp__stitch__get_project`, `mcp__stitch__list_screens`, `mcp__stitch__get_screen`) para obtener la pantalla de referencia.
- Tokens de color, tipografía y espaciado: usar los definidos en el EPEC Design System (`docs/EPEC Design System/`). Prioridad: Stitch → Design System → ningún default de framework.
- El agente `ui-designer` debe ser invocado antes de implementar cualquier pantalla nueva; es responsable de validar la coherencia visual con el diseño de Stitch.
- Prohibido usar el "look default" de cualquier framework (estilos out-of-the-box de Material UI, Tailwind defaults, etc.) sin mapearlos al Design System de EPEC.
- Inconsistencias o regresiones visuales respecto al diseño de Stitch deben corregirse antes de hacer commit.

## Context drift
- Al ~60% de la ventana de contexto: ejecutar `/compact`.
- Si la sesión es muy larga: decir "terminamos" → nueva sesión (el auto-bootstrap recarga todo).
