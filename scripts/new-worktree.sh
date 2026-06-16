#!/usr/bin/env bash
# new-worktree.sh — Crea un git worktree con naming convention del equipo
#
# Uso: scripts/new-worktree.sh feat/mi-feature
#      scripts/new-worktree.sh fix/el-bug
#
# Convención de nombres de rama:
#   feat/nombre-de-la-feature
#   fix/descripcion-del-bug
#   refactor/que-se-refactoriza
#   docs/que-documentacion
#   chore/tarea-de-mantenimiento
set -euo pipefail

BRANCH="${1:-}"

if [ -z "$BRANCH" ]; then
  echo "❌ Uso: scripts/new-worktree.sh <branch-name>"
  echo "   Ejemplos:"
  echo "     scripts/new-worktree.sh feat/nueva-feature"
  echo "     scripts/new-worktree.sh fix/corregir-bug"
  exit 1
fi

# Validar formato de la rama (Conventional Commits style)
VALID_PREFIXES=("feat" "fix" "refactor" "docs" "chore" "test" "perf")
PREFIX=$(echo "$BRANCH" | cut -d'/' -f1)

VALID=false
for p in "${VALID_PREFIXES[@]}"; do
  if [ "$PREFIX" = "$p" ]; then
    VALID=true
    break
  fi
done

if [ "$VALID" = false ]; then
  echo "⚠️  Prefijo '$PREFIX' no reconocido."
  echo "   Prefijos válidos: ${VALID_PREFIXES[*]}"
  echo "   ¿Continuar de todas formas? (s/N)"
  read -r CONFIRM
  if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    echo "Operación cancelada."
    exit 1
  fi
fi

# Directorio del worktree: ../[repo-name]-worktrees/[branch-slug]
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
BRANCH_SLUG=$(echo "$BRANCH" | tr '/' '-')
WORKTREE_DIR="${REPO_ROOT}/../${REPO_NAME}-worktrees/${BRANCH_SLUG}"

echo "==> Creando worktree..."
echo "    Branch: $BRANCH"
echo "    Directorio: $WORKTREE_DIR"
echo ""

# Crear branch y worktree
git worktree add -b "$BRANCH" "$WORKTREE_DIR" main

echo ""
echo "✅ Worktree creado."
echo ""
echo "Para trabajar en él, abrí UNA terminal separada y ejecutá:"
echo "  cd $WORKTREE_DIR"
echo "  claude"
echo ""
echo "Recordá: un worktree = un agente = una tarea = una rama."
echo "Máximo 2-3 worktrees activos en paralelo (restricción de RAM)."
