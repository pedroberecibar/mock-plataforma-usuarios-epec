# Skill: bdd-elicitor

## Propósito
Transformar requisitos ambiguos o incompletos en escenarios Gherkin (`Given/When/Then`) listos para ser la fuente de verdad del ciclo TDD. Cuestionar premisas antes de codificar.

## Principio

> **"Un requisito que no tiene un escenario de aceptación no existe todavía."**

El BDD Elicitor actúa antes de escribir cualquier código. Su output son archivos `.feature` en `docs/business_rules/`.

---

## Proceso de elicitación

Al recibir un requisito, seguir este proceso **siempre** antes de generar Gherkin:

### Paso 1 — Cuestionar premisas (5 preguntas mínimas)

1. **¿Quién** hace esto exactamente? (rol de usuario concreto, no "el sistema")
2. **¿Cuándo** ocurre? ¿Hay precondiciones no mencionadas?
3. **¿Qué pasa si** el dato de entrada está mal, vacío o fuera de rango?
4. **¿Qué pasa si** el sistema externo no responde?
5. **¿Cómo sabe el usuario** que la operación fue exitosa o falló?

Si alguna pregunta no tiene respuesta → **no escribir código**. Documentar la ambigüedad y pedirla al stakeholder.

### Paso 2 — Identificar escenarios

Para cada requisito, identificar:
- **Happy path** (el caso exitoso estándar)
- **Casos de error esperados** (validaciones, permisos, datos inválidos)
- **Edge cases** (vacío, límites, concurrencia, timeout)
- **Casos de negocio especiales** (excepciones a la regla, permisos extraordinarios)

### Paso 3 — Escribir Gherkin

```gherkin
Feature: [Nombre del comportamiento de negocio]
  Como [rol de usuario]
  Quiero [acción]
  Para [valor de negocio]

  # Happy path
  Scenario: [Descripción del caso exitoso]
    Given [estado inicial del sistema]
    And [condición adicional si aplica]
    When [acción del usuario]
    Then [resultado observable]
    And [resultado adicional si aplica]

  # Error case
  Scenario: [Descripción del caso de error]
    Given [estado inicial]
    When [acción con dato inválido]
    Then [mensaje de error o comportamiento defensivo]
```

### Paso 4 — Validar con el stakeholder

Antes de pasar a código: el Gherkin debe ser **leíble y aprobado por alguien no técnico**. Si el stakeholder no entiende un escenario, está mal escrito.

---

## Reglas de escritura

| ✅ Hacer | 🚫 No hacer |
|---------|------------|
| Usar lenguaje de negocio en Given/When/Then | Usar términos técnicos (`INSERT`, `HTTP 200`, `null`) |
| Un comportamiento por scenario | Agrupar múltiples cosas en un scenario |
| Scenarios independientes entre sí | Depender del orden de ejecución |
| Datos de ejemplo concretos | Datos vagos ("algún usuario", "un dato cualquiera") |
| Español rioplatense para el negocio | Mezclar idiomas en la misma feature |

---

## Ejemplo

**Requisito crudo:** "El sistema tiene que validar los partes diarios antes de aprobarlos."

**Preguntas:**
1. ¿Quién valida? ¿El auditor? ¿El sistema automáticamente?
2. ¿Qué se valida? ¿Fechas, importes, códigos EPEC?
3. ¿Qué pasa si un parte tiene datos incompletos?
4. ¿Qué pasa si el contratista ya fue rechazado antes?
5. ¿Cómo sabe el auditor que la validación fue exitosa?

**Output Gherkin (post-elicitación):**

```gherkin
Feature: Validación de partes diarios
  Como auditor
  Quiero validar un parte diario antes de aprobarlo
  Para asegurar que los datos del contratista son correctos

  Scenario: Parte con datos completos y correctos se aprueba
    Given un parte diario con código EPEC válido y fecha dentro del período
    And el contratista no tiene rechazos previos en el mismo período
    When el auditor hace clic en "Validar"
    Then el parte pasa a estado "Aprobado"
    And se registra el auditor y la fecha de aprobación en el historial

  Scenario: Parte con código EPEC inválido se rechaza automáticamente
    Given un parte diario con código EPEC que no existe en el catálogo
    When el auditor hace clic en "Validar"
    Then el sistema muestra el error "Código EPEC no reconocido: [código]"
    And el parte queda en estado "Revisión" sin cambiar

  Scenario: Parte duplicado detectado
    Given un parte diario con el mismo hash de operación que uno ya aprobado
    When el sistema procesa el lote
    Then el parte se marca como "Rechazado" con motivo "Duplicado"
    And se referencia el ID del parte original en la observación
```

---

## Output

Guardar los archivos `.feature` en `docs/business_rules/`.
Naming convention: `[dominio]-[comportamiento].feature` (ej: `partes-validacion.feature`).
