# Reglas de Negocio — Business Rules

Este directorio contiene los escenarios Gherkin que son la fuente de verdad del comportamiento del sistema.

Generados y mantenidos con la skill `bdd-elicitor` (`.claude/skills/bdd-elicitor/SKILL.md`).

## Convención de nombres

`[dominio]-[comportamiento].feature`

Ejemplos:
- `partes-validacion.feature`
- `lotes-ingestion.feature`
- `usuarios-autenticacion.feature`

## Principio

> Un requisito que no tiene un escenario de aceptación no existe todavía.

Antes de implementar cualquier funcionalidad, el escenario Gherkin correspondiente debe existir en este directorio y haber sido validado con el stakeholder.
