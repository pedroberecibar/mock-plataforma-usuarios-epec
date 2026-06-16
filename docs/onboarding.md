# Onboarding — Setup de máquina nueva

Guía paso a paso para configurar el entorno de desarrollo en una máquina nueva y estar listo para trabajar en menos de 30 minutos.

## Requisitos previos

| Herramienta | Versión mínima | Instalación |
|-------------|----------------|-------------|
| **Claude Code** | Última | `npm install -g @anthropic-ai/claude-code` |
| **Python** | 3.12+ | [python.org](https://www.python.org/downloads/) |
| **uv** | 0.4+ | `pip install uv` o `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Node.js** | LTS (20+) | [nodejs.org](https://nodejs.org) — solo para npx |
| **Lefthook** | Última | `go install github.com/evilmartians/lefthook@latest` o [releases](https://github.com/evilmartians/lefthook/releases) |
| **Git** | 2.35+ | Incluido en la mayoría de sistemas |
| **Obsidian** | Última | [obsidian.md](https://obsidian.md) — opcional pero recomendado |

> **Restricción EPEC:** el proxy TLS corporativo puede bloquear descargas directas. Si alguna instalación falla, usá el instalador offline o pedí la versión empaquetada al equipo.

---

## Pasos de instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/[org]/ai-dev-starter.git mi-proyecto
cd mi-proyecto
```

### 2. Correr el setup

```bash
bash scripts/setup.sh
```

El script:
- Instala los hooks de git (Lefthook)
- Crea el `.env` desde `.env.example`
- Crea el vault de Obsidian si no existe
- Instala dependencias Python con `uv`
- Instala commitlint via `npx`

Si algún paso falla por falta de permisos, el script te avisa e indica cómo hacerlo manualmente.

### 3. Configurar `.env`

```bash
# Editar .env y completar:
VAULT_PATH=/ruta/a/tu/obsidian-vault
```

El vault puede ser uno existente de Obsidian o el que creó el script en `~/Developer-Vault`.

### 4. Verificar Serena MCP

Serena es el servidor MCP de code graph (navegación semántica). Se configura en `.mcp.json` y se arranca automáticamente cuando abrís el proyecto con `claude`.

Requisito: `uvx` disponible (`uv` lo incluye).

```bash
# Verificar que uvx funciona:
uvx --version
```

### 5. Abrir el proyecto con Claude Code

```bash
claude
```

Claude va a leer `CLAUDE.md` automáticamente. Luego ejecutá:

```
/start-session
```

Eso carga `MEMORY.md` y `CONTEXT.md` y te orienta al estado actual del proyecto.

---

## Verificación rápida

```bash
# Tests pasan:
uv run pytest tests/ -q

# Linters pasan:
uv run ruff check src/
uv run mypy src/

# Hooks instalados:
lefthook run pre-commit --all-files
```

---

## Troubleshooting

### Proxy TLS bloquea instalaciones
- Usar `--proxy` en pip/npm si se soporta.
- Pedir el paquete offline al equipo.
- Para MCPs, verificar que los binarios se puedan descargar o empaquetar localmente.

### Lefthook no corre
```bash
lefthook install  # reinstalar hooks
git config core.hooksPath .git/hooks  # verificar path
```

### Serena no indexa el proyecto
- Verificar que `pyright` o `Intelephense` (según el stack) esté instalado.
- Apagar Ollama/Twinny mientras Serena indexa (restricción de RAM).
- Ver logs en la consola de Claude Code.

### `uv sync` falla sin permisos
```bash
# Alternativa: instalar en venv manual
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -e ".[dev]"
```
