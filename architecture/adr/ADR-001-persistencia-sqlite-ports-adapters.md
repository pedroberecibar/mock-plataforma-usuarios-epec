# ADR-001 — Persistencia SQLite y Ports & Adapters para cumplir Open/Closed

**Fecha:** 2026-06-16
**Estado:** Aceptado
**Decisores:** Equipo backend Plataforma de Clientes EPEC

---

## Contexto

El MVP de la Plataforma de Clientes EPEC necesita persistir consumo diario, objetivos de consumo y datos de vecinos, además de leer mediciones desde la fuente Oracle de EPEC y, más adelante, encolar tareas asíncronas, enviar notificaciones (push/email) y autenticar usuarios.

Para el MVP elegimos **SQLite** como motor de persistencia: no requiere levantar un servidor de base de datos, simplifica el setup local y de CI, y acelera el desarrollo. Conocemos su limitación: **escritura concurrente serializada (un solo writer) y ausencia de replicación**, lo que la hace inadecuada a escala. Es esperable migrar a Postgres (probablemente con PostGIS para el cálculo geográfico de vecinos) cuando el producto crezca.

La restricción de negocio es que **ese cambio futuro de tecnología no debe obligar a modificar la lógica de negocio**. Lo mismo aplica a cualquier otra dependencia externa (fuente Oracle, cola de tareas, proveedor de notificaciones, proveedor de auth): todas deben poder reemplazarse sin tocar los casos de uso.

## Decisión

**Elegimos:** SQLite para el MVP, accedido exclusivamente a través de **Ports & Adapters** (arquitectura hexagonal sobre las capas Clean Architecture ya definidas).

**Porque:** SQLite minimiza la fricción de desarrollo del MVP, y Ports & Adapters garantiza que esa elección sea reversible sin costo en la lógica de negocio, cumpliendo el Principio Open/Closed (abierto a extensión vía adapters nuevos, cerrado a modificación de los casos de uso).

Concretamente:

- **Los puertos son contratos `abc.ABC`** definidos en `application`/`domain`. Los casos de uso dependen del puerto (la abstracción), nunca de una implementación concreta.
- **Los adapters concretos viven en `infrastructure`** e implementan los puertos. La elección de tecnología (sqlite3/SQLAlchemy, cliente Oracle, Redis/Celery, SDK de push/email, librería de JWT) queda encapsulada acá y en ningún otro lado.
- **Ningún caso de uso importa una librería de infraestructura concreta.** El acoplamiento a SQLite (o a cualquier proveedor) existe solo dentro del adapter correspondiente.
- **Existe un composition root único**: un entrypoint en la raíz de `src/` (ej. `src/main.py`), *fuera de las cuatro capas*, que es el único lugar que importa `infrastructure` + `interface` y cablea (inyecta) los adapters concretos en los casos de uso. Migrar de tecnología = cambiar qué adapter se instancia en el composition root, más agregar el adapter nuevo en `infrastructure`. Nada más cambia.

  > Nota sobre ubicación del composition root: las reglas de capas enforced por `architecture/tests/test_clean_architecture.py` prohíben `interface → infrastructure` e `infrastructure → interface`. Por eso el composition root NO vive dentro de la capa `interface`, sino como entrypoint en la raíz de `src/`, que no pertenece a ninguna capa y por lo tanto no es chequeado por el fitness test. Así puede importar ambas capas para hacer el wiring sin violar la dirección de dependencias.

Puertos del proyecto (contratos abstractos):

| Puerto | Capa | Responsabilidad | Tecnología encapsulada en el adapter |
|--------|------|-----------------|--------------------------------------|
| `ConsumoDiarioRepository` | application/domain | Persistir/leer consumo diario | SQLite (MVP) → Postgres |
| `ObjetivoConsumoRepository` | application/domain | Persistir/leer objetivos de consumo | SQLite (MVP) → Postgres |
| `VecinosRepository` | application/domain | Resolver vecinos (radio 150 m) | SQLite + Haversine (MVP) → PostGIS |
| `MedicionSourceReader` | application/domain | Leer mediciones de la fuente EPEC | Cliente Oracle |
| `TaskQueue` | application/domain | Encolar tareas asíncronas | Redis/Celery (u otro) |
| `NotificationSender` | application/domain | Enviar notificaciones push/email | SDK del proveedor |
| `AuthProvider` | application/domain | Autenticar/autorizar usuarios | Librería de JWT / IdP |

## Alternativas consideradas

| Opción | Pros | Contras | Por qué se descartó |
|--------|------|---------|---------------------|
| ORM/SQLite directo en los casos de uso (sin abstracción) | Menos código, menos indirección inicial | Acopla la lógica de negocio a SQLite; migrar a Postgres obliga a modificar casos de uso | Viola Open/Closed y Dependency Inversion: la migración futura requeriría tocar código de negocio existente |
| Postgres + PostGIS desde el día uno | Sin migración futura; cálculo geográfico nativo (vecinos) | Requiere levantar servidor de DB en local y CI; mayor fricción de setup en el MVP | Penaliza la velocidad de desarrollo del MVP sin beneficio inmediato |
| SQLite + Ports & Adapters (elegida) | Setup mínimo; tecnología swappeable sin tocar negocio; testeable con adapters fake | Capa de indirección adicional; cálculo de vecinos en Python (Haversine) en vez de PostGIS | — |

## Consecuencias

**Positivas:**
- Los casos de uso se testean con **adapters fake/in-memory** que implementan los mismos puertos `abc.ABC`, sin tocar SQLite ni servicios externos.
- El swap de tecnología (SQLite→Postgres, Oracle→otra fuente, proveedor de cola/notificaciones/auth) se hace **agregando un adapter nuevo en `infrastructure`** y cambiando el wiring en el composition root: cero modificaciones en `application`/`domain`.
- El acoplamiento a cada tecnología queda aislado y localizado en un único adapter.

**Negativas / trade-offs aceptados:**
- Capa de indirección adicional: cada dependencia externa exige definir un puerto + al menos un adapter, aun cuando hoy haya una sola implementación.
- El cálculo de vecinos en un radio de 150 m se resuelve **en Python con la fórmula de Haversine** (dentro del adapter SQLite), en vez de usar operaciones geográficas nativas de PostGIS. Es aceptable para el volumen del MVP; se revisará al migrar a Postgres.

**Riesgos:**
- Puertos mal diseñados (con fugas de detalles de SQLite, p. ej. exponer SQL crudo o tipos del driver) anularían el beneficio. Mitigación: los puertos exponen entidades de `domain` y tipos del lenguaje, nunca artefactos del motor de persistencia; se valida en code review.
- Erosión de la regla con el tiempo (algún caso de uso importando infra directo). Mitigación: el fitness test `architecture/tests/test_clean_architecture.py` corre en CI y bloquea `application/domain → infrastructure`.

## Estado de implementación

Pendiente de implementación. Esta ADR es solo la decisión arquitectónica; no se modificó código fuente. Al implementar:
- Puertos (`abc.ABC`) en `src/application/` (o `src/domain/` según corresponda al contrato).
- Adapters concretos en `src/infrastructure/` (adapter SQLite primero).
- Composition root en `src/main.py` (raíz de `src/`, fuera de las capas).
- Se respetará el TDD obligatorio (ver CLAUDE.md): test en RED → adapter/caso de uso mínimo → refactor.
