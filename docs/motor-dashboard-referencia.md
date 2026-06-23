# Referencia: MotorDashboardPython

**Repo:** `git@github.com:PROTELEM-EPEC/MotorDashboardPython.git`  
**Rama activa:** `simuladorPGVC`  
**Stack:** Python · Streamlit · Oracle (oracledb) · Polars

Proyecto interno de EPEC orientado a analistas y grandes clientes. Consulta las tablas SIGEC de Oracle para analizar ítems de factura por suministro y período. Es el punto de referencia para entender la estructura de datos del sistema de facturación.

---

## Arquitectura (capas)

```
pages/ (Streamlit entry)
  └── src/ui/          ← render, caché, presenters
        └── src/app_services/   ← orquesta casos de uso
              ├── src/use_cases/  ← lógica pura, sin Oracle ni Polars
              ├── src/data/       ← OracleQueryExecutor, FileSqlRepository
              └── src/domain/     ← @dataclass frozen, sin dependencias
```

Misma filosofía que nuestra plataforma (Ports & Adapters). Sus casos de uso no importan Oracle directamente.

---

## Tablas Oracle clave

| Tabla | Contenido |
|---|---|
| `xxsigec.DOCUMENTOS` | Facturas (`DOC_TIPO='F'`). Columnas: `SRV_CODIGO`, `DOC_NUMERO`, `DOC_ANIO`, `DOC_PERIODO`. |
| `xxsigec.ITEMS` | Ítems de cada factura. Columnas: `DOC_NUMERO`, `DOC_TIPO`, `TIT_CLAVE`, `ITM_CANTIDAD`, `ITM_PRECIO_UNIT`, `ITM_IMPORTE`. |
| `xxsigec.TIPOS_ITEM` | Catálogo de tipos de ítem (`TIT_CLAVE`, `TIT_DESCRIPCION`, `TIT_DESCRIPCION_COMPLETA`). |
| `xxsigec.XXCO_LECTURAS_TELEMEDIDAS` | Lecturas de medidor (granularidad a confirmar). `CDR_CODIGO='E'` = energía. |
| `xxsigec.XXCO_LECTURAS_TELEMEDIDAS_H` | Ídem, posiblemente horaria o histórica (confirmar con el equipo). Usada en Sprint 1 de nuestra plataforma. |

---

## Claves de ítems de factura relevantes

### Energía (tramos horarios)

| TIT_CLAVE | Concepto | Relevancia para plataforma |
|---|---|---|
| `EPI` | Energía Pico | v2 — desglose kWh por tramo |
| `ERE` | Energía Resto | v2 — desglose kWh por tramo |
| `EVA` | Energía Valle | v2 — desglose kWh por tramo |

> **Decisión de producto (acordada con el jefe, 2026-06-22):** EPI/ERE/EVA queda diferida a v2. No implementar en MVP. No mostrar precios — solo kWh.

### Impuestos

| TIT_CLAVE | Concepto | % oficial |
|---|---|---|
| `OIM` | Ord. imp. municipal | 9.90% |
| `R27` | ERSeP-Ley 10281 R.27 | 0.10% |
| `FDE` | Fdo. Des. Ene. Prov. | 6.50% |
| `DGI` | Percep. RG 2408 - DGI | 3.00% |
| `IBC` | Percep. Ing. Brutos | 4.00% |
| `IVI` | IVA Inscripto | 27.00% |
| `DTO` | Dto. 2298 | 0.40% |

---

## Query principal de ítems por período

Archivo: `query/itemsXperiodo_factura.sql`

```sql
SELECT
    DOC.SRV_CODIGO,
    DOC.DOC_ANIO,
    DOC.DOC_PERIODO,
    itm.tit_clave,
    tit_descripcion,
    tit_descripcion_completa,
    sum(itm.itm_cantidad)    AS cantidad_total,
    itm.itm_precio_unit,
    sum(itm.itm_importe)     AS importe_total
FROM xxsigec.items itm, xxsigec.tipos_item itm_tipo, XXSIGEC.DOCUMENTOS DOC
WHERE itm_tipo.tit_clave = itm.tit_clave
  AND DOC.DOC_NUMERO = ITM.DOC_NUMERO
  AND DOC.DOC_TIPO   = ITM.DOC_TIPO
  AND (filtro de rango de períodos con binds :anio_desde/:anio_hasta/:periodo_desde/:periodo_hasta)
  AND DOC.SRV_CODIGO = :srv_codigo
  AND DOC.DOC_TIPO = 'F'
GROUP BY DOC.SRV_CODIGO, DOC.DOC_ANIO, DOC.DOC_PERIODO,
         itm.tit_clave, tit_descripcion, tit_descripcion_completa, itm.itm_precio_unit
```

Soporta múltiples suministros: el parameterizador reemplaza `:srv_codigo` por `IN (:srv_codigo_0, :srv_codigo_1, ...)`.

---

## Lógica de negocio reutilizable

### `ConstruirResumenFactura`

Agrupa los ítems por suministro y clasifica en tres categorías:
- `energia`: ítems EPI/ERE/EVA — calcula precio promedio ponderado (importe/cantidad)
- `impuestos_destacados`: OIM, R27, FDE — valida contra % oficial sobre base sin impuestos
- `otros_impuestos_percepciones`: DGI, IBC, IVI, DTO

### `ConstruirResumenMensualFactura`

Repite el resumen anterior agrupando por `(srv_codigo, doc_anio, doc_periodo)`.

### `build_items_period_query` / `build_items_period_parameters`

Parametriza la SQL para que soporte múltiples suministros y un rango de períodos mes a mes. Reutilizable directamente como patrón para futuras queries nuestras.

---

## Modelo de dominio

```python
@dataclass(frozen=True)
class InvoiceConcept:
    srv_codigo: int
    doc_anio: int
    doc_periodo: int
    tit_clave: str
    cantidad_total: Decimal | None   # kWh (EPI/ERE/EVA)
    itm_precio_unit: Decimal | None  # $/kWh
    importe_total: Decimal           # $

@dataclass(frozen=True)
class InvoiceSummary:
    srv_codigo: int
    total_factura: Decimal
    subtotal_energia: Decimal
    cantidad_total: Decimal          # total kWh (suma EPI+ERE+EVA)
    energia: list[EnergySummaryLine]
    impuestos_destacados: list[TaxSummaryLine]
    otros_impuestos_percepciones: list[TaxAnalysisLine]
```

---

## Cómo conectar Oracle (referencia cruzada)

Ver `docs/conexion_oracle_referencia.md` para el patrón de conexión con `oracledb` (thin/thick, reintentos, `SET TRANSACTION READ ONLY`). El Motor Dashboard usa exactamente ese patrón en `src/data/oracle_query_executor.py`.

---

## Qué incorporar a nuestra plataforma

| Feature | Estado | Notas |
|---|---|---|
| Consumo horario real | **Sprint 11 (planificado)** | Fuente: `XXCO_LECTURAS_TELEMEDIDAS_H`. Confirmar granularidad horaria. |
| Identificación hora pico | **Sprint 11 (planificado)** | Depende de consumo horario. |
| Desglose EPI/ERE/EVA (kWh) | v2 | Solo kWh, sin precios. |
| Precios $/kWh | **Descartado** | Decisión del jefe: no mostrar precios en la app. |
| Desglose de impuestos | **Descartado** | Implica montos. |
