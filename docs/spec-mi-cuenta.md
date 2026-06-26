# Spec — Sección "Mi cuenta" (backend)

> Estado: backlog-ready. Generado con `/spec` (gstack) el 2026-06-26.
> Alcance de este spec: **backend** — qué datos mostrar y de dónde tomarlos.
> El diseño de presentación / UI queda diferido a una segunda instancia.

## 1. Por qué (Fase 1)

- **Quién:** usuario final autenticado de la Plataforma de Clientes EPEC que entra a
  "Mi cuenta" para validar qué datos tiene EPEC sobre él. Todas las marcas de medidor
  (CLOU, NANSEN, CHUPETE, GC).
- **Comportamiento actual:** no existe la sección. Hoy solo se leen 6 campos Oracle
  (`suministro_meta_reader.py` sobre `GEOREF.VW_INTELIGENTES`) y en SQLite hay
  `usuarios.email` + `suministros`.
- **Comportamiento deseado:** un endpoint `GET /api/cuenta` (scopeado al usuario
  autenticado) que devuelve el perfil completo de la cuenta, agregando SQLite +
  Oracle, con PII tratada como dato sensible y degradado elegante cuando un campo
  falta.
- **Por qué ahora:** sección del MVP; dejar robusto el backend antes de diseñar UI.
- **Definición de hecho:** ver Criterios de aceptación (§6).

## 2. Hallazgos de la investigación Oracle (en vivo, read-only)

Verificado contra `SUMINISTRO=2817670` y una muestra de cada marca. Todas las
consultas con `SET TRANSACTION READ ONLY` + `rollback`.

### Fuente principal: `GEOREF.VM_INTELIGENTES` (TABLE, key `SUMINISTRO`)

98 columnas; en una fila trae casi todo lo que necesitamos:

| Dato | Columna | Tipo | Nulabilidad observada |
|---|---|---|---|
| Nombre / razón social | `RAZON_SOCIAL` | VARCHAR2(60) | 100% poblado (4 marcas) |
| Tipo de documento | `TIPO_DOCUMENTO` | VARCHAR2(3) | mayormente 'DNI' |
| Nro de documento (**PII**) | `NRO_DOCUMENTO` | NUMBER | CLOU 95 / NANSEN 97 / CHUPETE 96 / GC 17 % |
| CUIT (**PII**) | `CUIT` | NUMBER | suele estar cuando falta DNI (empresas/GC) |
| Calle | `CALLE` | VARCHAR2(100) | ~100% |
| Altura / Piso / Depto / Torre | `ALTURA` `PISO` `DEPTO` `TORRE` | mixto | parciales (muchos null en barrios cerrados) |
| Barrio / Localidad / CP | `BARRIO` `LOCALIDAD` `CP` | — | ~100% barrio/localidad |
| Datos adicionales domicilio | `DATOS_ADICIONALES_DOMICILIO` | VARCHAR2(60) | parcial |
| Nº de suministro | `SUMINISTRO` | NUMBER | clave |
| Marca del medidor | `TELEMEDIBLE` | VARCHAR2(7) | CLOU/NANSEN/CHUPETE/GC |
| Nº de medidor | `MEDIDOR` | VARCHAR2 | ~100% |
| Medidor inteligente desde | `TELEMEDIBLE_DESDE` | DATE | — |
| Código de tarifa | `CODIGO_TARIFA` | VARCHAR2(4) | NOT NULL ('140'=resid, '240'=comercial…) |
| **Tarifa legible** | `TARIFA` | VARCHAR2(40) | NOT NULL (ej. "1.a/f RESIDENCIAL") |
| Grupo tarifario | `GRUPO_TARIFARIO` | VARCHAR2(2) | NOT NULL |
| Clase | `CLASE` | VARCHAR2(3) | NOT NULL |
| Clase legible | `DESCRIPCION_CLASE` | VARCHAR2(30) | poblado (ej. "1 a-b-f Casas de familia") |
| Tensión | `TENSION` | VARCHAR2(5) | NOT NULL |
| Estado de servicio / contrato | `ESTADO_SERVICIO` `ESTADO_CONTRATO` | VARCHAR2(4) | NOT NULL |
| Coordenadas | `DC_LATITUD` `DC_LONGITUD` | NUMBER | — |

**Clave:** `TARIFA` y `DESCRIPCION_CLASE` ya son descriptores legibles — NO hace falta
una tabla de tarifas extra para el MVP. (`XXSIGEC.TARIFAS` existe si luego se quiere
más detalle.)

### Fase del medidor: `GEOREF.VM_SUMINISTROS` (key `SUMINISTRO`)

`VM_INTELIGENTES` **no** tiene la fase. Vive en `VM_SUMINISTROS.MEDIDOR_FASES`
(VARCHAR2(5)). Se obtiene con un LEFT JOIN por `SUMINISTRO`.

Dominio real del campo (a normalizar en el dominio):

| Valor crudo | n (aprox) | Normalizado |
|---|---|---|
| `MON` | 1.05M | Monofásico |
| `TRI` | 128k | Trifásico |
| `TRIF` | 28 | Trifásico |
| `0` | 11 | Desconocido |
| `NULL` | 25k | Desconocido |

### Cobertura por marca (LEFT JOIN VM_INTELIGENTES + VM_SUMINISTROS)

| Marca | Total | con DNI | con razón social | con calle | con medidor | con fase |
|---|---|---|---|---|---|---|
| CLOU | 146.977 | 95% | 100% | ~100% | 100% | 97% |
| NANSEN | 138.290 | 97% | 100% | ~100% | 100% | 97% |
| CHUPETE | 65.626 | 96% | 100% | ~100% | ~100% | 97% |
| GC | 4.309 | 17% | 100% | 99% | 100% | 98% |

Conclusión: el contrato funciona para **todas las marcas** con degradado elegante.
Para GC (empresas) el DNI suele faltar → fallback a CUIT.

## 3. Contrato de datos (DTO de respuesta)

`GET /api/cuenta` → `200 CuentaResponse`. Agrupado en 4 secciones. Campos sin dato
viajan `null` (la UI decide "No informado"). PII enmascarada por defecto.

```jsonc
{
  "personales": {
    "nombre_o_razon_social": "string",
    "tipo_documento": "DNI | null",
    "nro_documento_masked": "****1815 | null",   // últimos 4; nunca claro por defecto
    "cuit_masked": "**-********-3 | null",        // fallback identidad para GC/empresas
    "email": "string | null"                       // de usuarios.email (SQLite)
  },
  "suministro": {
    "numero": "SRV-2817670",
    "estado_servicio": "string | null",
    "direccion": "string (compuesta) | null",
    "barrio": "string | null",
    "localidad": "string | null",
    "cp": "string | null"
  },
  "tarifa": {
    "codigo": "140",
    "descripcion": "1.a/f RESIDENCIAL",
    "grupo_tarifario": "1",
    "clase": "1",
    "clase_descripcion": "1 a-b-f Casas de familia",
    "tension": "1 | null"
  },
  "medidor": {
    "numero": "string | null",
    "marca": "CLOU | NANSEN | CHUPETE | GC | null",
    "fase": "Monofásico | Trifásico | Desconocido",
    "inteligente_desde": "2023-03-10 | null"
  }
}
```

`direccion` compuesta = `CALLE [ALTURA] [Piso PISO] [Depto DEPTO] [Torre TORRE]`,
saltando los componentes null. `DATOS_ADICIONALES_DOMICILIO` se anexa si existe.

## 4. Diseño backend (arquitectura hexagonal — ADR-001)

Regla Open/Closed: **no** tocar `suministro_meta_reader.py` (lo usa la ingesta). Se
agrega un adapter nuevo.

### 4.1 Puerto nuevo (domain)
`domain/ports/cuenta_reader.py` → `CuentaReader(abc.ABC)`:
```python
async def leer_cuenta(self, suministro_id: str) -> CuentaSuministroRaw | None
```
`CuentaSuministroRaw` = dataclass frozen con los campos crudos de Oracle (incluye
`nro_documento` y `cuit` en claro, solo en memoria, nunca logueados).

### 4.2 Adapter Oracle
`infrastructure/oracle/cuenta_reader.py` — una query parametrizada:
```sql
SELECT i.RAZON_SOCIAL, i.TIPO_DOCUMENTO, i.NRO_DOCUMENTO, i.CUIT,
       i.CALLE, i.ALTURA, i.PISO, i.DEPTO, i.TORRE, i.BARRIO, i.LOCALIDAD, i.CP,
       i.DATOS_ADICIONALES_DOMICILIO, i.ESTADO_SERVICIO,
       i.TELEMEDIBLE, i.MEDIDOR, i.TELEMEDIBLE_DESDE,
       i.CODIGO_TARIFA, i.TARIFA, i.GRUPO_TARIFARIO, i.CLASE, i.DESCRIPCION_CLASE,
       i.TENSION, s.MEDIDOR_FASES
FROM   GEOREF.VM_INTELIGENTES i
LEFT JOIN GEOREF.VM_SUMINISTROS s ON s.SUMINISTRO = i.SUMINISTRO
WHERE  i.SUMINISTRO = :suministro_id
FETCH FIRST 1 ROW ONLY
```
`READ ONLY` + `rollback`, mismo patrón de timeout/executor que el reader actual.
`suministro_id` = `int(id.removeprefix("SRV-"))`.

### 4.3 Cifrado de PII en reposo (decisión: persistir cifrado)
- Puerto `domain/ports/pii_cipher.py` → `PiiCipher` (`encrypt(str)->str`, `decrypt(str)->str`).
- Adapter `infrastructure/crypto/fernet_cipher.py` con `cryptography.Fernet`, clave
  derivada de `SECRET_KEY` (ya en `.env`). Nunca hardcodear.
- Tabla nueva (migración Alembic) `cuenta_datos_sensibles`:
  `suministro_id PK/FK`, `nro_documento_enc`, `cuit_enc`, `actualizado_en`.
  Solo se almacenan valores **cifrados**; jamás texto claro.
- Repo `CuentaSensibleRepository` (puerto) + adapter SQLite.

### 4.4 Caso de uso
`application/use_cases/obtener_cuenta.py` → `ObtenerCuentaUseCase`:
1. `email` ← `usuario_repository`.
2. crudo ← `cuenta_reader.leer_cuenta(suministro_id)` (Oracle).
3. cifra `nro_documento`/`cuit` y hace upsert en `cuenta_datos_sensibles`.
4. compone el DTO: normaliza fase, arma dirección, enmascara PII.
5. degrada: si Oracle devuelve `None`, responde 404; si faltan campos, `null`.

### 4.5 Interface
- `interface/cuenta_router.py` → `GET /api/cuenta`. El `suministro_id` se obtiene del
  usuario autenticado vía `AuthProvider`; **nunca** se acepta del cliente.
- Registrar router en `main`.
- `frontend/vite.config.ts` → agregar `/api/cuenta` al `server.proxy` (regla conocida:
  sin esto el fetch falla en silencio).

### 4.6 Fakes para tests
`infrastructure/fakes/cuenta_reader.py`, `..._pii_cipher.py`, repo sensible fake.

## 5. Seguridad

- PII (`NRO_DOCUMENTO`, `CUIT`) cifrada en reposo (Fernet); enmascarada en la
  respuesta; valor en claro solo tras una acción explícita de "revelar" (fuera de
  alcance ahora — futura).
- Queries 100% parametrizadas (ya lo son).
- Endpoint scopeado al usuario autenticado; sin IDOR (no recibir `suministro_id` del
  cliente).
- PII nunca en logs ni en mensajes de error.
- El spec y los scripts de descubrimiento usan ejemplos enmascarados, no PII real.

## 6. Criterios de aceptación

1. `GET /api/cuenta` autenticado devuelve las 4 secciones para `SRV-2817670`.
2. Para una muestra de cada marca (CLOU/NANSEN/CHUPETE/GC) responde 200 con los
   campos disponibles; los faltantes son `null`, sin error.
3. GC sin DNI → `nro_documento_masked=null` y `cuit_masked` presente.
4. `fase` normalizada a Monofásico/Trifásico/Desconocido (incluye `TRIF`/`0`/null).
5. `nro_documento`/`cuit` nunca aparecen en claro en la respuesta ni en logs; en la
   tabla `cuenta_datos_sensibles` están cifrados (verificable: el valor en disco no
   es el número).
6. Sin usuario autenticado → 401; suministro inexistente en Oracle → 404.
7. TDD: cada pieza arranca por test en rojo (fake reader → cipher → use case →
   router). `ruff` + `mypy` limpios. Pre-commit nativo OK.

## 7. Fuera de alcance (este spec)

- Diseño de presentación / UI (segunda instancia: `ui-designer` + Stitch + validación
  en browser).
- Acción "revelar DNI en claro" con segundo factor / auditoría.
- Edición de datos por el usuario (esto es solo lectura/validación).
- Detalle de precios o ítems de factura (decisión: solo kWh en la plataforma).

## 8. Plan de implementación (orden sugerido, TDD)

1. Migración Alembic `cuenta_datos_sensibles` + repo SQLite (port + adapter + fake).
2. `PiiCipher` (port + Fernet adapter + fake) con tests de round-trip.
3. `CuentaReader` (port + fake) y `ObtenerCuentaUseCase` con fakes (lógica de
   composición, máscara, normalización de fase, degradado).
4. Adapter Oracle `cuenta_reader.py` (integración, gated por env Oracle).
5. `cuenta_router.py` + registro en `main` + proxy Vite.
6. `/review` y luego `/ship`.
