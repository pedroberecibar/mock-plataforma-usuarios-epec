# Catálogo de Patrones

Este directorio contiene fichas de referencia rápida de los patrones de diseño más usados en el proyecto.

Están optimizadas para ser leídas por `repomix --compress` como contexto de planificación.

## Estructura

Cada patrón tiene su propia ficha en `docs/patterns/[nombre]-pattern.md`.

## Patrones documentados

| Patrón | Archivo | Cuándo usar |
|--------|---------|-------------|
| Repository | `repository-pattern.md` | Acceso a datos desacoplado |
| Strategy | `strategy-pattern.md` | Variantes de algoritmo |
| Factory | `factory-pattern.md` | Creación variable de objetos |

> Agregar fichas a medida que se adoptan patrones en el proyecto real.
> Usar el agente `docs-updater` para mantener este catálogo al día.
