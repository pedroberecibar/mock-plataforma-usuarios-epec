# Skill: design-patterns

## Propósito
Guiar la elección del patrón de diseño correcto para cada situación, con sesgo explícito a **YAGNI** (You Aren't Gonna Need It). Ante la duda, preferir siempre la solución más simple.

## Principio rector: complejidad accidental vs. esencial

Antes de aplicar cualquier patrón, preguntarse:
> ¿Este patrón resuelve un problema **real y presente**, o anticipa uno futuro hipotético?

Si la respuesta es "futuro hipotético" → no aplicarlo todavía.

---

## Árbol de decisión principal

```
¿Necesito crear objetos?
  ├─ Los objetos varían por tipo y esa variación importa → FACTORY METHOD o ABSTRACT FACTORY
  ├─ La creación es compleja con muchos pasos → BUILDER
  └─ Necesito una única instancia global → SINGLETON (con cautela; preferir inyección)

¿Necesito variar comportamiento?
  ├─ Múltiples variantes de un algoritmo → STRATEGY
  ├─ Agregar comportamiento sin modificar clase → DECORATOR
  ├─ El comportamiento cambia según estado → STATE
  └─ Múltiples objetos reaccionan a un evento → OBSERVER / EVENT BUS

¿Necesito organizar acceso a datos?
  ├─ Desacoplar lógica de negocio de la BD → REPOSITORY
  ├─ Agrupar operaciones relacionadas → UNIT OF WORK
  └─ Separar lecturas de escrituras (alta complejidad) → CQRS (solo si la complejidad lo justifica)

¿Necesito simplificar una interfaz compleja?
  ├─ Sistema externo complicado → FACADE
  ├─ Incompatibilidad de interfaces → ADAPTER
  └─ Comunicación entre subsistemas → MEDIATOR
```

---

## Catálogo resumido

### ✅ Usar con confianza

| Patrón | Cuándo | Señal de que lo necesitás |
|--------|--------|--------------------------|
| **Repository** | Acceso a datos | Tenés `session.query(Model).filter(...)` disperso por toda la lógica de negocio |
| **Strategy** | Variantes de algoritmo | Aparece un `if tipo == "A": ... elif tipo == "B": ...` que crece |
| **Factory Method** | Creación variable | El constructor tiene lógica condicional de qué tipo instanciar |
| **Decorator** | Comportamiento adicional | Querés agregar logging/cache/retry sin tocar la clase original |
| **Observer** | Desacoplamiento de eventos | Múltiples componentes reaccionan a algo sin saber entre ellos |
| **Adapter** | Integración externa | Wrapper sobre SDK externo para no contaminar el dominio |

### ⚠️ Usar con criterio

| Patrón | Cuándo | Riesgo |
|--------|--------|--------|
| **CQRS** | Solo si lectura y escritura tienen modelos radicalmente distintos | Over-engineering brutal si no hay necesidad real |
| **Event Sourcing** | Solo si el historial de cambios es el negocio mismo | Complejidad operativa enorme |
| **Abstract Factory** | Solo si hay familias de objetos que varían juntas | Fácil de sobre-generalizar |

### 🚫 Anti-patrones: detectar y señalar

| Anti-patrón | Señal | Acción |
|-------------|-------|--------|
| **God Object** | Clase > 300 líneas con múltiples responsabilidades | Extraer: identificar las N responsabilidades, crear N clases |
| **Anemic Domain** | Clases de dominio solo con getters/setters, lógica en servicios | Mover lógica de negocio al dominio |
| **Premature Optimization** | Cachear/optimizar sin medir que hay un problema | Medir primero (`cProfile`, `time`) |
| **Speculative Generality** | "Por si acaso en el futuro necesitamos..." | YAGNI: implementar cuando sea necesario |
| **Service Locator** | `container.get("MiServicio")` disperso por el código | Usar inyección de dependencias explícita |
| **Magic Numbers** | Literales sin nombre (`if status == 3:`) | Constantes nombradas o enums |

---

## Reglas de extracción (cuándo dividir)

1. **Archivo > 300 líneas** → flag para extracción. Buscar responsabilidades.
2. **Función > 20 líneas** → candidata a extracción o descomposición.
3. **Más de 3 niveles de indentación** → señal de complejidad excesiva.
4. **El nombre de la clase/función usa "and" o "or"** → hace demasiadas cosas.
5. **Cambiar una cosa rompe tests no relacionados** → hay acoplamiento oculto.

---

## Proceso recomendado

1. Identificar el problema concreto (no el hipotético).
2. Buscar la solución más simple que lo resuelva.
3. Si el código resultante es difícil de testear → el diseño está acoplado. Refactorizar.
4. Si aparece duplicación > 5 líneas → abstracción. Si aparece una sola vez → dejarlo.
5. Documentar en MEMORY.md el patrón elegido y por qué.
