# Export para Notion — "Plataforma Clientes EPEC"

Esta carpeta contiene la documentación lista para cargarse en Notion bajo la página
**"Plataforma Clientes EPEC"** (id `37b62e87-5521-8001-ac13-d418201ab1aa`).

Se generó como Markdown porque **el MCP de Notion no está conectado en esta sesión**
(no hay herramientas `mcp__*Notion*` disponibles). Una vez habilitado, el contenido se
publica tal cual en las subpáginas.

## Estructura a crear en Notion

```
📄 Plataforma Clientes EPEC  (página existente)
 ├── 📄 MVP — Estado actual y casos de uso   ← MVP-estado-actual.md
 └── 📄 Versiones de la plataforma (Roadmap v2+)  ← versiones-roadmap.md
```

## Archivos

| Archivo | Destino en Notion |
|---|---|
| `MVP-estado-actual.md` | Subpágina **MVP — Estado actual y casos de uso** |
| `versiones-roadmap.md` | Subpágina **Versiones de la plataforma (Roadmap v2+)** |
| este README | No se publica; es guía de importación. |

## Nota sugerida para la página madre

> **Plataforma de Clientes EPEC** — App web responsive para que el cliente entienda y
> gestione su consumo eléctrico (kWh), con datos reales de Oracle. La documentación se
> organiza en dos subpáginas: el **MVP** (estado actual + casos de uso cubiertos) y las
> **Versiones futuras** (roadmap). *Última actualización: 2026-06-30.*
> La documentación previa ("Especificación técnica — Proyección mensual", "Plan de
> arquitectura — MVP") queda como material histórico; el estado vigente es el de estas
> subpáginas.

## Para publicar cuando Notion esté disponible

1. Habilitar el servidor MCP de Notion.
2. `notion-fetch` de la página madre y subpáginas existentes (diff contra este contenido).
3. Crear las dos subpáginas con el contenido de los `.md`.
4. Actualizar la nota/índice de la página madre y marcar la doc previa como histórica.

## Alcance explícito

- **Incluye:** producto, funcionalidad, casos de uso, arquitectura del sistema, orientación
  al estudio conductual (factura digital + brecha subsidio/RASE).
- **No incluye** (por pedido): workflow de desarrollo — MCP, herramientas, skills, agentes,
  hooks, TDD, runbooks de deploy.
