# Código de la aplicación

Este directorio se llena según el tipo de proyecto:

```
src/
├── backend/      # Python/FastAPI o PHP/Laravel
│   ├── domain/           # Entidades, value objects, reglas de negocio puras
│   ├── application/      # Use cases, servicios de aplicación
│   ├── infrastructure/   # DB, APIs externas, repositorios concretos
│   └── interface/        # FastAPI routers, CLI, adaptadores de entrada
└── frontend/     # UI con Tailwind v4 + shadcn/ui (si aplica)
```

## Reglas de arquitectura (enforced by CI)

La capa **Domain** nunca importa de **Infrastructure** ni **Interface**.
La capa **Application** nunca importa de **Infrastructure**.

Verificado automáticamente por `architecture/tests/test_clean_architecture.py`.

## Para empezar un proyecto nuevo

1. Definir el stack en `CLAUDE.md` (ya configurado).
2. Consultar la skill `design-patterns` antes de definir la estructura de módulos.
3. Si hay UI: consultar el agente `ui-designer` antes del primer componente.
4. Primer código = primer test en RED (skill `tdd-guide`).
