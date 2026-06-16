#!/usr/bin/env bash
# setup.sh — AI Dev Starter onboarding
# Instala y configura el entorno de desarrollo local.
# Degrada con gracia si no hay permisos admin o faltan herramientas.
set -euo pipefail

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║       AI Dev Starter — Setup             ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ---------------------------------------------------------------------------
# 1. Lefthook (git hooks runner)
# ---------------------------------------------------------------------------
echo "==> [1/5] Lefthook (git hooks)..."
if command -v lefthook > /dev/null 2>&1; then
  lefthook install && echo "    ✅ lefthook hooks instalados"
else
  echo "    ⚠️  lefthook no encontrado."
  echo "       Instalá con: go install github.com/evilmartians/lefthook@latest"
  echo "       O descargá el binario en: https://github.com/evilmartians/lefthook/releases"
  echo "       Una vez instalado, corré: lefthook install"
fi

# ---------------------------------------------------------------------------
# 2. .env desde plantilla
# ---------------------------------------------------------------------------
echo ""
echo "==> [2/5] Variables de entorno..."
if [ -f .env ]; then
  echo "    ℹ️  .env ya existe. No se sobreescribe."
else
  cp .env.example .env
  echo "    ✅ .env creado desde .env.example"
  echo "    ⚠️  Completá VAULT_PATH en .env antes de usar el MCP de Obsidian."
fi

# ---------------------------------------------------------------------------
# 3. Vault de Obsidian
# ---------------------------------------------------------------------------
echo ""
echo "==> [3/5] Vault de Obsidian..."
if [ -f .env ]; then
  # shellcheck disable=SC1091
  source .env 2>/dev/null || true
fi
VAULT="${VAULT_PATH:-$HOME/Developer-Vault}"
if [ -d "$VAULT" ]; then
  echo "    ℹ️  Vault ya existe en $VAULT"
else
  mkdir -p "$VAULT"/{Projects,Research,Templates,Archive}
  echo "    ✅ Vault creado en $VAULT"
  echo "       Estructura: Projects/ Research/ Templates/ Archive/"
fi

# ---------------------------------------------------------------------------
# 4. Dependencias Python (uv)
# ---------------------------------------------------------------------------
echo ""
echo "==> [4/5] Dependencias Python..."
if [ -f pyproject.toml ]; then
  if command -v uv > /dev/null 2>&1; then
    uv sync --dev && echo "    ✅ Dependencias Python instaladas con uv"
  else
    echo "    ⚠️  uv no encontrado."
    echo "       Instalá con: pip install uv"
    echo "       O: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "       Luego corré: uv sync --dev"
  fi
else
  echo "    ℹ️  No hay pyproject.toml en la raíz. Saltando dependencias Python."
fi

# ---------------------------------------------------------------------------
# 5. Node.js (solo para npx MCP + commitlint)
# ---------------------------------------------------------------------------
echo ""
echo "==> [5/5] Node.js (npx para MCP y commitlint)..."
if command -v node > /dev/null 2>&1; then
  NODE_VERSION=$(node --version)
  echo "    ✅ Node.js $NODE_VERSION detectado"
  if command -v npm > /dev/null 2>&1; then
    npm install --save-dev @commitlint/cli @commitlint/config-conventional 2>/dev/null \
      && echo "    ✅ commitlint instalado" \
      || echo "    ⚠️  No se pudo instalar commitlint (puede que no haya package.json)"
  fi
else
  echo "    ⚠️  Node.js no encontrado."
  echo "       Instalá desde: https://nodejs.org (LTS recomendado)"
  echo "       Node es necesario solo para: npx commitlint y npx @modelcontextprotocol/server-filesystem"
fi

# ---------------------------------------------------------------------------
# Resumen final
# ---------------------------------------------------------------------------
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║           Setup completado               ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Próximos pasos:"
echo "  1. Completá .env con VAULT_PATH=/ruta/a/tu/vault"
echo "  2. Abrí el proyecto con: claude"
echo "  3. En Claude Code, corré: /start-session"
echo ""
