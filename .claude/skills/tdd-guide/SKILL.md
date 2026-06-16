# Skill: tdd-guide

## Propósito
Guiar el ciclo Red-Green-Refactor en proyectos Python (pytest) y PHP (Pest). Asegurar que NUNCA se escribe implementación antes de un test que falla.

## El ciclo TDD obligatorio

```
RED   → Escribir UN test que defina el comportamiento esperado. Correrlo. Confirmar que falla.
GREEN → Escribir la implementación MÍNIMA que hace pasar ese test. Nada más.
REFACTOR → Mejorar calidad (naming, extracción, simplificación). Todos los tests siguen verde.
```

## Reglas inquebrantables

1. **Test primero, siempre.** Si no hay un test fallando, no hay implementación.
2. **Los tests definen comportamiento, no implementación.** No reflejar la lógica interna en los asserts; testear outcomes.
3. **Cobertura no es calidad.** No generar tests después para "tapar" cobertura. Un test sin aserciones útiles es ruido.
4. **Un test a la vez.** No escribir múltiples tests simultáneamente; rompe el ciclo.
5. **El refactor no agrega funcionalidad.** Si el test nuevo requiere más código → nuevo ciclo RED.

## Scripts disponibles

### `tdd_workflow.py`
Valida que el archivo que se está por escribir/editar tiene un test correspondiente en estado RED antes de proceder.

```bash
python .claude/skills/tdd-guide/scripts/tdd_workflow.py --check path/al/archivo.py
```

### `coverage_analyzer.py`
Detecta tests sin aserciones, tests que solo cubren happy-path, y funciones sin cobertura.

```bash
python .claude/skills/tdd-guide/scripts/coverage_analyzer.py
```

## Comandos de referencia

Adaptá al test runner del stack definido en `CLAUDE.md`:

```bash
# Python (pytest)
pytest tests/ -v
pytest tests/test_mi_modulo.py::test_nombre -v
pytest tests/ --cov=src --cov-report=term-missing
pytest tests/ --lf -v   # solo fallando

# Node.js / TypeScript (Jest / Vitest)
npx jest --verbose
npx jest --testPathPattern=mi_modulo
npx vitest run --coverage

# PHP (Pest)
./vendor/bin/pest --verbose
./vendor/bin/pest --coverage --min=80
./vendor/bin/pest --bail

# Ruby (RSpec)
bundle exec rspec spec/
bundle exec rspec spec/mi_spec.rb

# Go
go test ./... -v
go test -run TestNombre ./...
```

## Anti-patrones a detectar y señalar

| Anti-patrón | Señal | Qué hacer |
|-------------|-------|-----------|
| Implementation-first | No hay test fallando antes de editar `src/` | Parar. Escribir el test. |
| Test-after | "Agrego tests para subir cobertura" | Rechazar. Los tests deben guiar el diseño. |
| God test | Un test verifica 10 comportamientos distintos | Dividir en tests unitarios independientes. |
| Mock everything | Mockear hasta las clases propias | Revisar si el diseño tiene demasiado acoplamiento. |
| Happy-path only | Solo se testean casos exitosos | Agregar casos de error, edge cases, límites. |

## Árbol de decisión para dudas comunes

```
¿Tengo que escribir código nuevo?
  └─ ¿Hay un test en RED que lo requiere?
       ├─ Sí → Escribir implementación mínima (GREEN)
       └─ No → Escribir el test primero (RED)

¿El test pasa pero el código es feo?
  └─ REFACTOR: mejorar sin agregar funcionalidad
       └─ ¿Todos los tests siguen verde? → Continuar
       └─ ¿Algún test rompió? → Revertir y repensar
```
