# Referencia: API pública de facturación de EPEC

**Descubierto:** 2026-06-26 (inspección de Network en la web oficial de EPEC).
**Fuente:** `https://www.epec.com.ar/tramites/pagos` (SPA pública de pagos de EPEC).

Hallazgo clave: la web oficial de EPEC obtiene los **datos reales de la factura a pagar
(vencimiento + importe)** con una **apiKey pública en texto plano** (`web-prod`). Esto
permite mostrar la factura dentro de nuestra propia plataforma, no solo redirigir.

> ⚠️ Es una API **no documentada/no oficial** (uso interno del frontend de EPEC). Puede
> cambiar sin aviso. Tratarla como fuente externa volátil detrás de un puerto (ADR-001).

---

## 1. Autenticación

| Header | Valor | Notas |
|---|---|---|
| `apiKey` | `web-prod` | Key **pública** del frontend de EPEC. Viaja en texto plano. Suficiente para leer documentos. |
| `Authorization` | *(vacío)* | No se usa. No hace falta token de usuario. |

El código del proyecto lee la key de `EPEC_API_KEY` y cae a `web-prod` por defecto
(ver `src/infrastructure/epec/epec_factura_verificacion.py`).

---

## 2. Endpoints

### 2a. Validar contrato (lo que YA usábamos — NO trae factura)

```
GET https://www.epec.com.ar/api/contratos/no-ov/{contrato}/{cliente}
```
- Orden: **contrato primero, cliente segundo**.
- `200 OK` con **body vacío** (`content-length: 0`) ⇒ contrato válido.
- `404` ⇒ contrato no encontrado / orden invertido.
- **Solo valida existencia. No devuelve vencimiento ni importe.** Por esto el código viejo
  nunca pudo mostrar el vencimiento real.

### 2b. Documentos a pagar (EL HALLAZGO — trae vencimiento + importe)

```
POST https://www.epec.com.ar/api/documentos/a-pagar
Content-Type: application/json
apiKey: web-prod

{"contratoId":"0281767003","clienteId":"1109294"}
```

- **Nombres de campo exactos del body: `contratoId` y `clienteId`** (NO `contrato`/`cliente`
  ni `numeroContrato`/`numeroCliente` → esos dan `400`).
- Devuelve `200` con JSON real (gzip).

#### Respuesta (ejemplo real, suministro de prueba contrato `0281767003` / cliente `1109294`)

```json
{
  "habilitado": "S",
  "pagoOnlineHabilitado": "S",
  "pagoEfectivoHabilitado": "S",
  "financiacionHabilitada": "S",
  "libreDeudaHabilitado": "N",
  "pagoParcialHabilitado": "N",
  "resitriccionId": 0,
  "mensajeInhabilitado": "- Verifica <a href=\"...segmentacion/0281767003/1109294\">aquí</a> tu situación de subsidio.",
  "documentosAPagar": [
    {
      "id": "F708669297",
      "periodo": "07/2026",
      "importe": "             133,372.90",
      "tipoDocumento": "Factura",
      "documento": "0007 - 08669297",
      "vencimiento": "30/06/2026",
      "estado": "pagar",
      "mensaje": "Pago a término sin recargo hasta su vencimiento",
      "urlDocumento": "/api/reportes/<hash-largo>",
      "urlDetalle": null,
      "clasificacion": "DocAPagar",
      "imagenLectura": "N",
      "telemedicion": "S",
      "desde": "12052026",
      "hasta": "10062026",
      "infoAdicional": " "
    }
  ],
  "documentosFinanciados": []
}
```

#### Mapeo de campos relevantes

| Campo JSON | Formato | Uso en plataforma |
|---|---|---|
| `documentosAPagar[].vencimiento` | `DD/MM/YYYY` | Fecha de vencimiento real (reemplaza el fake `hoy+5`). |
| `documentosAPagar[].importe` | string con padding, `,` miles `.` decimal (`"   133,372.90"`) | Importe a pagar. Requiere `.strip()` + parseo `es-AR`. |
| `documentosAPagar[].periodo` | `MM/YYYY` | Período facturado. |
| `documentosAPagar[].estado` | `"pagar"` / etc. | Estado del documento. |
| `documentosAPagar[].urlDocumento` | path relativo `/api/reportes/<hash>` | PDF de la factura (anteponer `https://www.epec.com.ar`). |
| `pagoOnlineHabilitado` | `"S"`/`"N"` | Habilitar/ocultar botón de pago online. |

---

## 3. Otros recursos derivados

- **PDF de la factura:** `https://www.epec.com.ar` + `urlDocumento`.
- **Situación de subsidio/segmentación:**
  `https://www.epec.com.ar/oficina-virtual/mis-tramites/segmentacion/{contrato}/{cliente}`.
- **Página de pago (manual):** `https://www.epec.com.ar/tramites/pagos` (el usuario tipea
  contrato/cliente).
- **Deep-link NO disponible (confirmado 2026-06-26):**
  `?contrato=...&cliente=...` ignora los query params y muestra el formulario vacío;
  `/tramites/pagos/{contrato}/{cliente}` da 404. Además, al completar el flujo y llegar a
  la pantalla de pago, la URL **sigue siendo** `/tramites/pagos` (sin params) y un **F5
  rebota al formulario**: el SPA guarda contrato/cliente en memoria, no en la URL. No hay
  forma de precargar la factura por URL, y no se puede escribir el sessionStorage de
  epec.com.ar desde otro origen (cross-origin). **Máximo alcance del botón: redirigir al
  formulario** (el usuario tipea contrato/cliente). Mitigación posible: mostrarle al usuario
  sus números de cliente/contrato en nuestra pantalla para copiar-pegar.
- **Embeber el pago es inviable:** las respuestas de EPEC traen `X-Frame-Options: DENY`
  ⇒ no se puede iframe. El pago debe abrirse en pestaña nueva en el sitio de EPEC
  (ventaja: no tocamos dinero ni datos de tarjeta, cero responsabilidad PCI).

---

## 4. Estado en NUESTRO código (al 2026-06-26)

- `/factura/datos` (lo que consume la pantalla "Mi Factura") está cableado al **fake**
  `FakeFacturaSourceReader()` en `src/main.py` → devuelve `hoy + 5 días`. **No es real.**
- El puerto correcto a implementar es `FacturaSourceReader` (`get_factura(suministro_id)`).
- `EpecFacturaVerificacion` ya le pega a EPEC pero al endpoint **2a** (solo validación).

### Para mostrar datos reales (adapter pendiente)
1. Nuevo adapter `infrastructure/epec/epec_documentos_source_reader.py` que implemente
   `FacturaSourceReader` pegándole a **2b** (`/api/documentos/a-pagar`).
2. Cablearlo en `src/main.py` reemplazando `FakeFacturaSourceReader()` (sin tocar caso de
   uso ni router — ADR-001).
3. Ampliar `FacturaResult` para incluir `importe`, `periodo`, `url_pdf`, `pago_online` si se
   quiere mostrar el monto (hoy el MVP es "sin montos").

### ✅ RESUELTO: cómo obtener `contratoId` + `clienteId` desde el suministro (verificado E2E 2026-06-26)

El endpoint 2b necesita `contratoId` (10 díg.) + `clienteId`, ambos **derivables del suministro
con una sola query a Oracle** `GEOREF.VW_INTELIGENTES` (la vista que ya usamos para "Mi cuenta",
ojo: el adapter actual consulta `VM_INTELIGENTES`, pero `VW_INTELIGENTES` tiene estas columnas):

```sql
SELECT CLIENTE, SUMINISTRO, CONTRATO
FROM   GEOREF.VW_INTELIGENTES
WHERE  SUMINISTRO = :suministro    -- :suministro = int sin prefijo SRV-
```

Para `SUMINISTRO=2817670` devuelve `CLIENTE=1109294`, `CONTRATO=3`.

**Construcción de los IDs:**
```python
cliente_id  = str(CLIENTE)                                   # "1109294"
# contratoId = suministro + contrato(2 díg.), todo rellenado a 10 díg. con ceros a la izquierda
contrato_id = (str(SUMINISTRO) + str(CONTRATO).zfill(2)).zfill(10)   # "0281767003"
```
Regla del contrato: concatenar `SUMINISTRO` + `CONTRATO` (este último a 2 dígitos); si el
resultado tiene < 10 dígitos, rellenar con ceros al inicio hasta 10.

**Verificación end-to-end real (2026-06-26):** suministro `2817670` → query Oracle →
`clienteId=1109294`, `contratoId=0281767003` → `POST /api/documentos/a-pagar` →
`200` con factura real (período 07/2026, **venc. 30/06/2026, importe 133.372,90**, estado "pagar").

> `VW_INTELIGENTES.CLIENTE` ya trae el cliente directo, así que **no hace falta** la tabla
> `XXSIGEC.XXCO_PRS_IIBB` (donde el cliente vive en `PRS_NUMERO`; su `SRV_CODIGO` NO es el
> suministro de GEOREF, así que esa tabla es más difícil de joinear). Queda como referencia
> alternativa pero la vía simple es `VW_INTELIGENTES`.

**Persistencia (recomendado):** cachear `cliente_id` + `contrato_id` por suministro (la tabla
vacía `factura_redireccion` ya tiene columnas `numero_cliente`/`numero_contrato`) para no pegarle
a Oracle en cada request. Refrescar en onboarding o por job.

---

## 5. Reproducción rápida (curl/httpx)

```python
import httpx, json
url = "https://www.epec.com.ar/api/documentos/a-pagar"
hdr = {"content-type": "application/json", "apiKey": "web-prod",
       "Origin": "https://www.epec.com.ar", "Referer": "https://www.epec.com.ar/tramites/pagos"}
body = json.dumps({"contratoId": "0281767003", "clienteId": "1109294"}, separators=(",", ":"))
r = httpx.post(url, headers=hdr, content=body, timeout=20.0)
print(r.json()["documentosAPagar"][0]["vencimiento"])  # -> "30/06/2026"
```
