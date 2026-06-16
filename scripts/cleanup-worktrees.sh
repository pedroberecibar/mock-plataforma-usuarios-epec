#!/usr/bin/env bash
# cleanup-worktrees.sh — Lista y limpia worktrees ya mergeados
#
# Uso: scripts/cleanup-worktrees.sh [--dry-run]
set -euo pipefail

DRY_RUN=false
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=true
  echo "ℹ️  Modo dry-run: no se elimina nada."
fi

echo "==> Worktrees activos:"
git worktree list
echo ""

# Obtener ramas mergeadas a main
MERGED=$(git branch --merged main | grep -v "^\*" | grep -v "^  main$" | sed 's/^  //')

if [ -z "$MERGED" ]; then
  echo "✅ No hay ramas mergeadas para limpiar."
  exit 0
fi

echo "==> Ramas mergeadas a main que se pueden limpiar:"
echo "$MERGED"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "ℹ️  (dry-run) Se eliminarían: $MERGED"
  exit 0
fi

echo "¿Eliminar estas ramas y sus worktrees? (s/N)"
read -r CONFIRM
if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
  echo "Operación cancelada."
  exit 0
fi

while IFS= read -r BRANCH; do
  # Buscar worktree asociado a la rama
  WORKTREE=$(git worktree list --porcelain | grep -A2 "branch refs/heads/$BRANCH" | grep "worktree" | awk '{print $2}' || true)

  if [ -n "$WORKTREE" ] && [ "$WORKTREE" != "$(git rev-parse --show-toplevel)" ]; then
    echo "  Removiendo worktree: $WORKTREE"
    git worktree remove "$WORKTREE" --force
  fi

  echo "  Eliminando rama: $BRANCH"
  git branch -d "$BRANCH"
done <<< "$MERGED"

echo ""
echo "✅ Limpieza completada."
git worktree list
