# Estado de Sesión Actual

## Última sesión
- **Fecha:** 2026-06-26
- **Rama:** `spike/oracle-perfiles-georef`
- **Qué se completó:**
  - **Hallazgo API factura EPEC:** la web oficial trae vencimiento+importe reales vía
    `POST /api/documentos/a-pagar` (apiKey pública `web-prod`, body `{contratoId,clienteId}`).
    Los IDs se derivan del suministro con `GEOREF.VW_INTELIGENTES` (CLIENTE + CONTRATO);
    `contratoId = (suministro + contrato.zfill(2)).zfill(10)`. Documentado en
    `docs/epec-factura-api-referencia.md`. Probado E2E con 12 suministros reales.
  - **Feature factura real (TDD, hexagonal):** puerto `FacturaIdentificadores`
    (reader Oracle + cache SQLite), adapter `EpecDocumentosSourceReader`, `FacturaResult`
    ampliado (importe/periodo/url_pdf/pago_online), router propaga campos, cableado en
    `main.py` (real cuando Oracle disponible, fake si no). Migración `c3d4e5f6a7b8`
    (factura_redireccion.suministro_id). Frontend: importe + botón "Pagar mi factura" + PDF.
  - **Rediseño UI Objetivos:** full-width alineado a la sección Consumo (paleta contenida).
  - **Integración Mi cuenta (otro agente):** wiring pendiente en archivos compartidos
    (main.py, models.py, dependencies.py) unificado y commiteado junto con factura.
- **Verificación:** backend 407 tests · ruff + mypy limpios · frontend 161 tests · tsc + build OK.
  Cadena de migraciones lineal (single head c3d4e5f6a7b8), aplica limpia en DB fresca.
- **Qué quedó incompleto:**
  - Validación visual en browser de "Mi Factura": el proceso de Vite quedó trabado
    (pantalla en blanco hasta en login); el build de producción pasa limpio, así que es
    estado del dev server, no del código. Reiniciar Vite + backend (con env Oracle) para
    ver datos reales en vivo.
  - Deep-link a pagos de EPEC no precarga contrato/cliente (probado); el botón redirige
    al portal y el usuario tipea. Iframe inviable (X-Frame-Options: DENY).
  - Diseño de UI de "Mi cuenta" (endpoint backend ya listo en `/cuenta`).
- **Decisiones técnicas no documentadas:** —
- **Primer paso para la próxima sesión:** reiniciar dev servers y validar "Mi Factura" en
  browser con datos reales; luego encarar la UI de "Mi cuenta".
- **Tests fallando intencionalmente:** Ninguno.

## Estado del repo
Ver `git log --oneline -5` tras el commit de unificación.
