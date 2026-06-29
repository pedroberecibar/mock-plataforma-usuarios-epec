# Runbook — Deploy de la demo `mock-platform` (GitHub Pages)

> Contexto y decisiones: ver `architecture/adr/ADR-002-entornos-y-fuentes-de-datos.md`.
> Esta demo sirve un **snapshot estático de datos reales** del suministro `2817670`
> (Palacios, casa del owner). "Estático" ≠ "sintético": el dato es real, solo congelado.

Este runbook es para un agente/operador **sin contexto previo**. Seguilo en orden y revisá
la sección de Troubleshooting ante cualquier síntoma: los 5 bloqueos de abajo ya nos pasaron.

---

## Arquitectura del deploy (cómo encaja)

- El build de demo (`npm run build:demo`) usa `frontend/vite.config.gh-pages.ts`, que
  **aliasa por regex** cada import `../api/<módulo>` hacia `../mock/<módulo>`. Así, sin tocar
  el código fuente, la app deja de pegarle al backend y lee de los mocks.
- Los `mock/*.ts` devuelven datos: algunos hardcodeados, otros leen JSON de
  `frontend/public/mock-data/*.json` vía `mock/_fixtures.ts`.
- Esos JSON los genera `scripts/generate_mock_fixtures.py` desde la DB real
  (`SUMINISTRO_ID = "SRV-2817670"`). Se **commitean** al repo.
- `.github/workflows/deploy-demo.yml` corre `build:demo` y publica `frontend/dist` a la
  rama `mock-platform` del repo externo `pedroberecibar/mock-plataforma-usuarios-epec`.
  **CI NO regenera fixtures** (no alcanza Oracle, que es interno): solo buildea lo commiteado.

```
Oracle (interno)
   │  (solo en la máquina del owner)
   ▼
data/plataforma_clientes.db ──generate_mock_fixtures.py──▶ frontend/public/mock-data/*.json  (commit)
                                                                      │
                                                          git push main → deploy-demo.yml
                                                                      │  npm run build:demo (alias api→mock)
                                                                      ▼
                                                          frontend/dist → rama mock-platform → GitHub Pages
```

---

## Procedimiento

### 1. Refrescar el snapshot real (solo en la máquina con acceso a Oracle)

**Comando único** (orquesta ingesta + regeneración):

```sh
uv run python scripts/refresh_demo.py     # aborta si Oracle no está configurado
```

Equivale a correr, en orden:

```sh
uv run python scripts/seed_vecinos_reales.py            # respeta INGEST_EQUIPOS del .env (incluye 91013486 = 2817670)
uv run python scripts/generate_mock_fixtures.py         # escribe frontend/public/mock-data/*.json
```

### 2. Verificar el build de demo localmente

```sh
cd frontend
cmd /c "npm run build:demo"     # ⚠️ ver Bloqueo 1: el cmd /c es el workaround de permisos corporativos
cmd /c "npm run preview"        # opcional: revisar en http://localhost:4173 con base /mock-plataforma-usuarios-epec/
```

### 3. Commit + push (dispara el deploy)

```sh
git add frontend/public/mock-data/ frontend/src/mock/
git commit -m "chore(demo): refresh snapshot 2817670"
git push origin main            # deploy-demo.yml publica a mock-platform automáticamente
```

---

## Invariantes que NO hay que romper

1. **Paridad de mocks ↔ API real.** Por cada módulo en `src/api/*.ts` que la UI use en la
   demo, debe existir `src/mock/<mismo-nombre>.ts` **con la misma firma y los mismos tipos**
   (`src/api/types.ts` es la fuente de verdad). Si agregás un endpoint nuevo al frontend,
   agregá su mock Y su entrada en el regex (ver Bloqueo 3).
2. **Forma de los JSON = interfaces de `types.ts`.** Los fixtures deben respetar la
   estructura **anidada** (`HomeResponse`, `ComparacionResponse`, etc.), no aplanada
   (ver Bloqueo 5). Generalos con `generate_mock_fixtures.py`, no a mano.
3. **Privacidad:** de los vecinos solo se publican agregados ≥5 (`promedio`, `n_vecinos`),
   nunca consumo individual ni IDs.
4. **Objetivo no nulo** en `mock/objetivos.ts` (ver Bloqueo 2), o la demo entra en loop de
   onboarding.

---

## Troubleshooting — bloqueos conocidos (2026-06)

| # | Síntoma | Causa raíz | Solución |
|---|---------|-----------|----------|
| 1 | `npm run build:demo` falla con error de permisos en la terminal | Políticas de seguridad corporativas (red/máquina) bloquean los scripts de npm al invocarlos directo | **Envolver con el intérprete nativo de Windows:** `cmd /c "npm run build:demo"`. Aplica a cualquier comando npm bloqueado. (Relacionado: nota de memoria *npm bloqueado / hooks nativos*.) |
| 2 | Tras loguear, la demo entra en **loop infinito de onboarding** en vez de ir al dashboard | `mock/objetivos.ts` devolvía `null` por defecto → el router cree que el usuario no completó onboarding y lo redirige eternamente | Hacer que `fetchObjetivo` devuelva un objetivo válido (ej. `{ valor_kwh: 300, origen: "sugerido", vigente_desde: "..." }`). Ya aplicado en `mock/objetivos.ts`. |
| 3 | En GitHub Pages la app sigue llamando a `/api/...` reales y falla con **404 de red** pese a existir el mock | El regex de `vite.config.gh-pages.ts` no incluía el módulo nuevo, así que Vite no aliasaba esa ruta a `mock/` | Agregar el módulo al regex: `find: /\/api\/(home\|consumo\|objetivos\|factura\|alertas\|auth\|usuario\|ingest)/`. **Cada endpoint nuevo del frontend hay que sumarlo acá.** |
| 4 | La sesión no renderiza tras login (faltan datos del usuario) | La UI espera campos (`nombre`, `nro_suministro`, …) que la vieja `LoginResponse` mockeada no tenía | Mapear 1:1 los tipos que pide la UI (`src/api/types.ts`) en `mock/auth.ts` (y `mock/usuario.ts` para el perfil). Ya aplicado. |
| 5 | **Pantalla en blanco** + `Cannot read properties of undefined (reading 'total_kwh')` | Los JSON estáticos estaban **aplanados**; la UI espera objetos **anidados** (`home.consumo_mes.total_kwh`) | Respetar la jerarquía de `src/api/types.ts` (`HomeResponse`, `ComparacionResponse`). Generar los fixtures con `generate_mock_fixtures.py` (que ya produce la forma correcta) en vez de editarlos a mano. Para rastrear el campo roto: buscar (grep) dónde se consume, p. ej. `total_kwh`, y leer su interfaz. |

---

## Checklist rápido antes de pushear la demo

- [ ] Fixtures regeneradas con `generate_mock_fixtures.py` (no editadas a mano)
- [ ] `cmd /c "npm run build:demo"` pasa sin errores (tsc + vite)
- [ ] Todo `api/*` usado en demo tiene su `mock/*` con firma equivalente
- [ ] Todo endpoint nuevo está en el regex de `vite.config.gh-pages.ts`
- [ ] `mock/objetivos.ts` devuelve objetivo no nulo
- [ ] Fixtures sin consumo individual de vecinos (solo agregados ≥5)
