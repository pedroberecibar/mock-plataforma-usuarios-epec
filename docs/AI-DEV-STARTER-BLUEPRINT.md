# AI Dev Starter — Blueprint Definitivo

**Repositorio:** `ai-dev-starter`
**Equipo:** Desarrollo — Pedro Berecibar Studio / EPEC
**Versión del blueprint:** 1.0
**Fecha:** Junio 2026
**Propósito:** Documento maestro que Claude Code usa para generar, en local, toda la estructura del repositorio starter: carpetas, skills, agentes, configuración de MCPs, hooks, CI y README. Una vez generado y subido a GitHub, el equipo solo hace `git clone` / `git pull` para arrancar un proyecto nuevo sin reconfigurar nada.

---

## 0. Cómo usar este documento (instrucciones para Claude Code)

Este archivo es la **fuente de verdad**. Cuando se te pida materializar el starter:

1. Leé este documento completo antes de crear nada.
2. Generá la estructura de carpetas de la sección **§4** exactamente como está.
3. Creá cada archivo de configuración con el contenido base de la sección **§6**.
4. Creá las skills y agentes de las secciones **§7** y **§8**.
5. Generá el `README.md` raíz a partir de la sección **§9**.
6. Corré `scripts/setup.sh` mentalmente para validar que las rutas existen; no instales binarios globales sin confirmación del usuario.
7. **Antes de fijar versiones de cualquier herramienta de terceros**, verificá la versión y el estado actual del repo (stars, último release, breaking changes). Los números de los informes de origen pueden estar desactualizados; no los copies como verdad.

**Principio rector:** todo open-source con tracción real, ejecución local/offline siempre que se pueda, cero dependencia de servicios cloud para el núcleo. El proxy TLS corporativo de EPEC y el hardware modesto (16 GB RAM, sin GPU dedicada) son restricciones de primera clase.

---

## 1. Decisiones de stack (resueltas)

Los dos informes de origen divergen en varias herramientas. Acá quedan resueltas priorizando **estabilidad > eficiencia > novedad**. Donde había dos candidatos fuertes, se elige uno como primario y el otro queda documentado como alternativa, no se instalan ambos.

| Capa | Elección primaria | Alternativa documentada | Por qué |
|------|-------------------|-------------------------|---------|
| Agente principal | Claude Code (nativo) | — | Skills, hooks, subagentes y worktrees nativos. Sin framework de orquestación externo. |
| Code graph / navegación semántica | **Serena MCP** (`oraios/serena`) | GitNexus | Serena usa LSP (Python: pyright; PHP: Intelephense), permite edición a nivel de símbolo y refactor seguro sin reemplazos de texto frágiles. Más estable y menos destructivo que un grafo solo-lectura. Offline. |
| Empaquetado de contexto estático | **Repomix** (`yamadashy/repomix`) con `--compress` | Aider repo-map | Comprime el repo vía Tree-sitter (firmas, no implementaciones). Genera artefacto liviano para tareas de planificación. Complementa a Serena, no compite. |
| TDD enforcement | **Hook `PreToolUse` propio + skill `tdd-guide`** | TDD Guard; obra/superpowers | Se prioriza un hook simple y auditable que el equipo controla, más una skill que documenta el ciclo Red-Green-Refactor. No se adopta un framework pesado de orquestación TDD hasta validarlo. |
| Test runner Python | **pytest** | — | Trazas de aserción claras, arranque rápido. |
| Test runner PHP/Laravel | **Pest** | PHPUnit | Sintaxis expresiva, menos verbosidad = menos tokens. |
| Arquitectura Python | **ArchUnitPython** + **deptry** | import-linter | Fitness functions ejecutables en pytest, cero deps runtime. `deptry` detecta deps no declaradas. |
| Arquitectura PHP | **Deptrac** | phpat | Config YAML legible por el agente, estándar de la industria. |
| Arquitectura JS/TS | **dependency-cruiser** | — | Reglas de Clean Architecture verificables en CI. |
| Git hooks | **Lefthook** | Husky + lint-staged | Go, paralelo, sin Node.js → alivia RAM en hardware modesto. Un único YAML. |
| Commits | **Conventional Commits + commitlint** | — | Semver y changelog automáticos. |
| Secrets scanning | **trufflehog** + **secretlint** | — | En pre-commit (lefthook) y en CI. `.env` nunca al repo. |
| Continuidad de sesión | **CLAUDE.md + MEMORY.md + CONTEXT.md** (3 archivos) | auto-memory de Claude Code | Patrón validado, compartido vía Git, auditable. La auto-memory es personal y complementa. |
| Knowledge base / "cerebro" | **Obsidian** | — | Vault local. Método PARA, no Zettelkasten. |
| MCP de Obsidian | **`@modelcontextprotocol/server-filesystem` sobre el vault** | obsidian-local-rest-api; mcpvault | Se elige el filesystem MCP oficial por máxima estabilidad y compatibilidad detrás del proxy TLS, sin depender de plugins de terceros ni de que Obsidian esté abierto. Las otras dos quedan documentadas para evaluar si se necesita edición quirúrgica (vault_patch). |
| Memoria persistente MCP | **filesystem MCP (vault)** | mcp-sqlite local; server-memory oficial | El vault ya cubre persistencia. Se evita agregar otro servidor salvo necesidad real. |
| Linting Python | **ruff** + **mypy** | — | Un binario reemplaza flake8/black/isort. |
| CI | **GitHub Actions** | — | Tests + linters + arch checks + security. Sin agentes en CI (costo de tokens). |
| Orquestación multiagente | **subagentes nativos de Claude Code** | CrewAI/AutoGen/LangGraph | Cero overhead, sin RAM extra, control explícito. |

**Herramientas explícitamente descartadas** y por qué: CrewAI/AutoGen/LangGraph (sobre-ingeniería y RAM para equipo chico), Letta/mem0 (demasiado pesados), DeepGraph/mcp-code-graph cloud (requiere API externa, inaceptable bajo proxy TLS), wrappers no mantenidos de Obsidian.

> Nota de verificación: los informes de origen citan métricas de popularidad y versiones que conviene confirmar antes de fijar (`obra/superpowers`, `gstack`, números de stars, "Claude 3.5"). Tratá esos datos como pendientes de validar, no como hechos.

---

## 2. Restricciones de entorno (de primera clase)

- **Hardware:** 16 GB RAM, gráficos integrados, sin GPU dedicada. Todo corre en CPU. Máximo 2–3 worktrees/agentes en paralelo. Apagar Ollama/Twinny mientras se indexa con Serena o se corre Claude Code pesado.
- **Red:** proxy TLS corporativo. Todo MCP del núcleo funciona offline. Nada del núcleo depende de endpoints externos.
- **Seguridad:** empresa pública del sector energético. Secrets jamás en repo ni en `CLAUDE.md`. Scanning en pre-commit y CI. Datos sensibles permanecen locales.
- **Sin privilegios admin garantizados:** el `setup.sh` debe degradar con gracia si no puede instalar binarios globales (avisar y dar instrucciones manuales, no fallar en silencio).

---

## 3. Convenciones del equipo

- **Idioma:** comentarios y nombres técnicos en **inglés**; lógica de negocio, ADRs y contenido operativo en **español rioplatense**.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`...).
- **Branching:** GitHub Flow. `main` + feature branches de vida corta. Un worktree = un agente = una rama = una tarea.
- **TDD obligatorio:** Red → Green → Refactor. Nunca implementación antes de un test que falla. Nunca tests escritos después para "tapar" cobertura.
- **PRs:** plantilla obligatoria con checklist. Reviewer crítico (idealmente modelo distinto al autor).

---

## 4. Estructura de carpetas del starter

```
ai-dev-starter/
├── README.md                       # Onboarding: qué hay en cada carpeta y cómo arrancar
├── CLAUDE.md                       # Reglas permanentes del proyecto para Claude Code
├── MEMORY.md                       # Conocimiento arquitectónico acumulado (vacío al inicio)
├── CONTEXT.md                      # Estado de la sesión actual (lo actualiza Claude al cerrar)
├── AGENTS.md                       # Manual estático de los subagentes especializados
├── .gitignore
├── .env.example                    # Plantilla de variables; el .env real NUNCA se commitea
│
├── .claude/
│   ├── settings.json               # Hooks PreToolUse/PostToolUse, permisos
│   ├── skills/
│   │   ├── session-bootstrap/      # /start-session: carga CLAUDE.md + MEMORY.md + CONTEXT.md + git status
│   │   │   └── SKILL.md
│   │   ├── session-handoff/        # /end-session: escribe CONTEXT.md y nota al vault
│   │   │   └── SKILL.md
│   │   ├── tdd-guide/              # Ciclo Red-Green-Refactor + scripts pytest/pest
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── tdd_workflow.py
│   │   │       └── coverage_analyzer.py
│   │   ├── design-patterns/        # Heurísticas de cuándo aplicar cada patrón (anti over-engineering)
│   │   │   └── SKILL.md
│   │   ├── bdd-elicitor/           # Elicitación de reglas de negocio en Gherkin
│   │   │   └── SKILL.md
│   │   └── frontend-design/        # Design tokens, anti "Claude default look"
│   │       └── SKILL.md
│   └── agents/
│       ├── code-reviewer.md        # Revisor crítico de PRs (usa Serena para blast radius)
│       ├── security-reviewer.md    # OWASP / STRIDE / secrets, mentalidad adversarial
│       ├── ui-designer.md          # Diseño con token system, identidad por proyecto
│       └── docs-updater.md         # Mantiene ADRs y vault al día
│
├── .mcp.json                       # MCPs del proyecto: serena + vault (filesystem)
│
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       ├── ci.yml                  # tests + ruff + mypy + arch checks
│       ├── security.yml            # trufflehog + secretlint
│       └── release.yml             # semantic-release (changelog + tags)
│
├── architecture/
│   ├── tests/
│   │   ├── test_clean_architecture.py     # reglas ArchUnitPython (Python)
│   │   └── dependency-cruiser.config.js   # reglas dependency-cruiser (JS/TS)
│   └── adr/
│       └── ADR-000-template.md
│
├── docs/
│   ├── onboarding.md               # setup de máquina nueva paso a paso
│   ├── git-workflow.md             # branching + worktrees + naming
│   ├── agent-roles.md              # qué hace cada agente y cuándo invocarlo
│   ├── patterns/                   # catálogo estático de patrones (lo lee repomix --compress)
│   └── business_rules/             # archivos BDD/Gherkin validados
│
├── src/                            # código de la app (se llena por proyecto)
│   ├── backend/                    # Python/FastAPI o PHP/Laravel
│   └── frontend/                   # UI con Tailwind v4 + tokens corporativos
│
├── tests/                          # suite de tests (área primaria del ciclo TDD)
│
├── lefthook.yml                    # git hooks: pre-commit (ruff, secretlint, arch), commit-msg (commitlint)
├── commitlint.config.js
├── deptrac.yaml                    # fronteras entre módulos PHP (si aplica)
├── repomix.config.json             # directivas de compresión/exclusión para empaquetado de contexto
├── pyproject.toml                  # ruff, mypy, pytest, deptry (proyecto Python)
│
└── scripts/
    ├── setup.sh                    # onboarding: instala lefthook, serena, repomix; configura .mcp.json
    ├── new-worktree.sh             # crea worktree + branch con naming convention
    ├── cleanup-worktrees.sh        # lista y limpia worktrees mergeados
    └── capture_decision.py         # hook PostToolUse: append de decisiones al vault
```

> Adaptación por proyecto: un proyecto **solo Python** no necesita `deptrac.yaml` ni `commitlint.config.js` con reglas de front; uno **solo PHP** invierte la simetría. El starter trae todo; `setup.sh` pregunta el tipo de proyecto y desactiva lo que no aplica.

---

## 5. Flujo end-to-end

```
git clone ai-dev-starter
        │
        ▼
scripts/setup.sh
  ├─ instala lefthook (hooks de git)
  ├─ instala/registra serena MCP (offline, LSP)
  ├─ configura .mcp.json (serena + vault filesystem)
  ├─ crea Developer-Vault si no existe
  └─ degrada con aviso si no hay permisos admin
        │
        ▼
cd proyecto && claude
  ├─ Claude lee CLAUDE.md (auto)
  ├─ Claude lee MEMORY.md (auto)
  └─ /start-session → lee CONTEXT.md + git status
        │
        ▼
¿feature nueva?  ──sí──►  scripts/new-worktree.sh feat/nombre
        │                        │
        no                       ▼
        │                 Claude en worktree aislado (terminal aparte)
        ▼                        │
   trabajo en main ◄─────────────┘
        │
        ▼
Ciclo TDD:  RED (test falla) → hook lo verifica → GREEN (mínimo) → REFACTOR
        │
        ▼
lefthook pre-commit:  ruff · mypy · ArchUnitPython/Deptrac/depcruise · secretlint · tests
        │
        ▼
commit (Conventional) → lefthook commit-msg → commitlint
        │
        ▼
git push → CI (tests + lint + arch + security scan)
        │
        ▼
PR con template → security-reviewer + code-reviewer (blast radius vía Serena)
        │
        ▼
merge a main → semantic-release (CHANGELOG + tag)
        │
        ▼
/end-session → Claude actualiza CONTEXT.md + nota al vault
        │
        ▼
git worktree remove · git branch -d feat/nombre
```

---

## 6. Contenido base de los archivos de configuración

### 6.1 `CLAUDE.md` (raíz)

```markdown
# Reglas del proyecto para Claude Code

## Stack
- Backend: Python 3.12 (FastAPI) y/o PHP 8.x (Laravel)
- Frontend: Tailwind v4 + shadcn/ui
- Tests: pytest (Python), Pest (PHP)

## Idioma
- Código, nombres y comentarios técnicos: inglés
- Lógica de negocio, ADRs, contenido operativo: español rioplatense

## TDD Protocol (OBLIGATORIO)
1. RED: escribí un test que falle. Corrélo. Confirmá que falla. NO escribas implementación todavía.
2. GREEN: escribí la implementación MÍNIMA que pasa el test. Nada más.
3. REFACTOR: mejorá calidad. Todos los tests siguen en verde tras cada cambio.
4. NUNCA escribas tests que reflejen la lógica de implementación. Los tests definen comportamiento.
5. NUNCA generes tests después para satisfacer métricas de cobertura.

## Architecture Rules (enforced by CI)
- Single Responsibility: una razón para cambiar por clase/función. Archivo > 300 líneas → flag para extracción.
- Open/Closed: extendé con clases/funciones nuevas, no modificando existentes. Strategy/Decorator sobre cadenas if/else.
- Dependency Inversion: dependé de abstracciones. La capa domain NO importa infraestructura (verificado por ArchUnitPython/Deptrac).
- DRY: nada de bloques duplicados > 5 líneas.
- YAGNI: implementá solo lo necesario AHORA. Sin generalización especulativa.

## Seguridad
- NUNCA hardcodear secrets. NUNCA incluir credenciales en este archivo.
- Queries SQL siempre parametrizadas.

## Git
- Conventional Commits. GitHub Flow. Worktrees para trabajo paralelo.
```

### 6.2 `.mcp.json`

```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"]
    },
    "vault": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${VAULT_PATH}"]
    }
  }
}
```
> `VAULT_PATH` se define en `.env` (no en el repo). Verificá el comando de arranque actual de Serena antes de fijarlo.

### 6.3 `.claude/settings.json` (hooks)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "python .claude/skills/tdd-guide/scripts/tdd_workflow.py --check $CLAUDE_TOOL_INPUT_PATH" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python scripts/capture_decision.py \"$CLAUDE_TOOL_OUTPUT\"" }
        ]
      }
    ]
  }
}
```

### 6.4 `lefthook.yml`

```yaml
pre-commit:
  parallel: true
  commands:
    ruff:
      glob: "*.py"
      run: ruff check {staged_files}
    mypy:
      glob: "*.py"
      run: mypy {staged_files}
    arch-python:
      glob: "*.py"
      run: pytest architecture/tests/ -q
    deptrac:
      glob: "*.php"
      run: vendor/bin/deptrac analyse --no-progress
    secretlint:
      run: npx secretlint {staged_files}
    trufflehog:
      run: trufflehog git file://. --since-commit HEAD --only-verified --fail

commit-msg:
  commands:
    commitlint:
      run: npx commitlint --edit {1}
```

### 6.5 `commitlint.config.js`

```javascript
module.exports = { extends: ["@commitlint/config-conventional"] };
```

### 6.6 `repomix.config.json`

```json
{
  "output": { "filePath": "docs/codemap.xml", "style": "xml", "compress": true },
  "ignore": { "useGitignore": true, "customPatterns": ["tests/**", "**/*.lock", ".venv/**", "node_modules/**"] }
}
```

### 6.7 `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## Qué cambia

## Checklist
- [ ] Tests escritos ANTES de la implementación (TDD)
- [ ] ArchUnitPython / Deptrac / depcruise pasan sin errores
- [ ] Conventional Commits en todos los commits
- [ ] CONTEXT.md actualizado con decisiones tomadas
- [ ] Sin secrets hardcodeados (trufflehog/secretlint OK)
- [ ] Cobertura no bajó del umbral
```

### 6.8 `scripts/setup.sh` (esqueleto)

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "==> AI Dev Starter setup"

# 1. Lefthook (intenta global, degrada a local)
if command -v lefthook >/dev/null 2>&1; then
  lefthook install
else
  echo "!! lefthook no encontrado. Instalalo: https://github.com/evilmartians/lefthook (o 'go install')."
fi

# 2. .env desde plantilla
[ -f .env ] || cp .env.example .env && echo "==> .env creado desde .env.example (completá VAULT_PATH)"

# 3. Vault de Obsidian
VAULT="${VAULT_PATH:-$HOME/Developer-Vault}"
mkdir -p "$VAULT"/{Projects,Research,Templates}
echo "==> Vault en $VAULT"

# 4. Dependencias Python del proyecto (si hay pyproject.toml)
[ -f pyproject.toml ] && (command -v uv >/dev/null 2>&1 && uv sync || echo "!! uv no encontrado, instalá deps manualmente")

echo "==> Listo. Abrí el proyecto con: claude"
```

---

## 7. Skills a generar

Cada skill vive en `.claude/skills/<nombre>/SKILL.md`. Contenido base:

- **`session-bootstrap`** — al invocar `/start-session`: lee CLAUDE.md, MEMORY.md, CONTEXT.md y corre `git status` + `git log --oneline -10`. Resume el estado en una frase y propone el primer paso.
- **`session-handoff`** — al invocar `/end-session`: actualiza CONTEXT.md con (1) qué se completó (archivos/funciones concretos), (2) qué quedó incompleto y por qué, (3) decisiones técnicas no documentadas aún, (4) qué hacer primero la próxima sesión, (5) tests fallando a propósito. Append a la nota del día en el vault.
- **`tdd-guide`** — documenta el ciclo Red-Green-Refactor y trae `tdd_workflow.py` (valida fase y orden test/implementación) y `coverage_analyzer.py` (detecta tests sin aserciones y solo-happy-path). Scripts en stdlib pura, sin deps.
- **`design-patterns`** — árbol de decisión de cuándo usar cada patrón (Factory, Repository, Strategy, Observer, CQRS...) y anti-patrones a marcar (God Object, Anemic Domain, premature optimization). Sesgo explícito a YAGNI.
- **`bdd-elicitor`** — toma requisitos ambiguos y los convierte en escenarios Gherkin (`Given/When/Then`), cuestionando premisas y casos límite antes de codificar. Output a `docs/business_rules/`.
- **`frontend-design`** — copia adaptada de la skill `frontend-design` del entorno. Obliga a definir token system (4–6 colores hex nombrados, 2–3 tipografías con roles) antes de codear; prohíbe el "Claude default look".

---

## 8. Agentes a generar

Cada agente vive en `.claude/agents/<nombre>.md` con frontmatter `name` + `description`.

- **`code-reviewer`** — revisa PRs con mentalidad crítica, no aprueba por default. Usa Serena para análisis de blast radius (qué rompe el cambio). Output estructurado de hallazgos.
- **`security-reviewer`** — mentalidad adversarial. OWASP Top 10 + STRIDE. Detecta SQL injection, secrets, path traversal. Output por severidad: CRÍTICO / ALTO / MEDIO / BAJO / INFORMATIVO. Si está limpio, dice "CLEAN" con justificación.
- **`ui-designer`** — define identidad visual única por proyecto. Token system antes de código. Prohíbe gradients morados sin justificación e Inter como única fuente. Auto-crítica final: ¿se confunde con cualquier otro output?
- **`docs-updater`** — mantiene ADRs y el vault al día. Se puede disparar por hook PostToolUse cuando se toca un archivo de dominio.

---

## 9. README.md raíz (a generar)

El README debe explicar, en español rioplatense, **qué hay en cada carpeta y para qué sirve**, más los detalles del entorno. Estructura:

1. **Qué es esto** — repo starter para arrancar proyectos con workflow IA estandarizado; clone/pull y a trabajar.
2. **Requisitos** — Claude Code, Python 3.12 + uv, Node.js (solo para npx de MCP/commitlint), Lefthook, Obsidian. Hardware/red asumidos (16 GB RAM, proxy TLS, sin GPU).
3. **Quick start** — `git clone` → `scripts/setup.sh` → completar `.env` → `claude` → `/start-session`.
4. **Mapa del repositorio** — tabla carpeta-por-carpeta:
   - `.claude/skills/` → habilidades reutilizables (TDD, sesiones, BDD, diseño).
   - `.claude/agents/` → revisores especializados (código, seguridad, UI, docs).
   - `.mcp.json` → conexiones MCP (Serena para code graph, vault para conocimiento).
   - `architecture/` → fitness functions; las reglas que el código no puede violar.
   - `docs/` → onboarding, git workflow, ADRs, reglas de negocio, codemap.
   - `src/` y `tests/` → código y suite de tests del proyecto.
   - `lefthook.yml` → qué corre antes de cada commit.
   - `scripts/` → automatización (setup, worktrees, captura de decisiones).
   - `CLAUDE.md / MEMORY.md / CONTEXT.md` → el sistema de continuidad de contexto.
5. **Workflow diario** — el flujo de §5 resumido.
6. **Cómo agregar una skill/agente nuevo** — playbook corto.
7. **Entorno configurado** — versiones fijadas, MCPs activos, restricciones corporativas.
8. **Troubleshooting** — proxy TLS, Serena no indexa, lefthook no corre, permisos admin.

---

## 10. Roadmap de adopción

**Fase 1 — MVP (semanas 1–2):** generar el starter, CLAUDE.md con reglas del equipo, lefthook básico (ruff + commitlint), Serena en un proyecto real, vault con filesystem MCP, skills `session-bootstrap`/`session-handoff`/`tdd-guide`, `setup.sh`. *Éxito:* clonar y tener entorno funcionando en < 30 min.

**Fase 2 — consolidación (mes 1):** hook TDD en proyecto Python real, ArchUnitPython/Deptrac sobre módulos reales, agentes `security-reviewer`/`code-reviewer`/`docs-updater`, GitHub Actions (CI + security + release), templates de PARA en el vault. *Éxito:* todos los PRs pasan por template; el hook intercepta al menos un caso implementation-first.

**Fase 3 — maduración (trimestre 1):** primer par de worktrees paralelos reales, mutation testing en CI con umbral, skill `bdd-elicitor` en un requerimiento real, captura automática de decisiones al vault, playbook de "cómo agregar una skill". *Éxito:* el equipo extiende el starter sin asistencia externa; baja medible de defectos post-merge.

---

## 11. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Secrets filtrados por un agente | trufflehog + secretlint en pre-commit y CI; `.env` fuera del repo; sin credenciales en CLAUDE.md |
| Proxy TLS bloquea MCPs | Núcleo 100% offline (Serena local, vault filesystem); nada del núcleo requiere internet |
| Tests AI de baja calidad | Hook TDD + mutation testing en CI + review humano de la suite |
| RAM insuficiente con agentes paralelos | Máx 2–3 worktrees; apagar Ollama al indexar con Serena |
| Context drift en sesiones largas | Patrón de 3 archivos + `/compact` al ~60% del contexto; sesiones cortas |
| Loop de complacencia entre agentes | Reviewer con modelo distinto al autor; checklist obligatorio en PR |
| Versiones de herramientas desactualizadas | Pinear en config; revisar releases; **verificar antes de fijar** (los datos de los informes pueden estar viejos) |
| Sin permisos admin | `setup.sh` degrada con avisos e instrucciones manuales, no falla en silencio |

---

*Fin del blueprint. Claude Code: usá este documento como fuente de verdad para materializar el starter.*
