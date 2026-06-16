# Git Workflow — Branching, Worktrees y Naming

## Modelo: GitHub Flow

`main` siempre deployable. Todo trabajo en feature branches de vida corta.

```
main ──────────────────────────────────────────► (siempre verde)
       │                              │
       └─► feat/nueva-feature ──────►│ (PR + merge)
       └─► fix/corregir-bug ─────────│ (PR + merge)
```

---

## Naming convention de ramas

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Feature nueva | `feat/descripcion-corta` | `feat/validacion-partes` |
| Fix de bug | `fix/que-se-corrige` | `fix/hash-duplicado` |
| Refactor | `refactor/que-modulo` | `refactor/repositorio-lotes` |
| Docs | `docs/que-se-documenta` | `docs/adr-patron-cqrs` |
| Chore | `chore/tarea` | `chore/actualizar-deps` |
| Test | `test/que-se-testea` | `test/cobertura-exportador` |

Reglas:
- Kebab-case, sin mayúsculas, sin espacios.
- Descripción concreta (qué resuelve, no qué cambia).
- Vida útil máxima: 2-3 días. Si dura más, partir en tareas más chicas.

---

## Worktrees para trabajo paralelo

Un worktree = un agente = una rama = una tarea.

```bash
# Crear worktree para una feature nueva
bash scripts/new-worktree.sh feat/mi-feature

# El worktree queda en ../[repo]-worktrees/feat-mi-feature/
# Abrirlo en una terminal separada:
cd ../ai-dev-starter-worktrees/feat-mi-feature
claude
```

### Restricción de hardware
Máximo **2-3 worktrees activos en paralelo**. Con 16 GB RAM, más de eso degrada el rendimiento.

Si Claude Code + Serena están indexando, apagar Ollama/Twinny mientras tanto.

### Limpiar worktrees mergeados
```bash
bash scripts/cleanup-worktrees.sh        # interactivo
bash scripts/cleanup-worktrees.sh --dry-run  # preview sin eliminar
```

---

## Commits: Conventional Commits

Formato: `<tipo>(<scope opcional>): <descripción en imperativo>`

```
feat(partes): agregar validación de código EPEC
fix(lotes): corregir hash que incluía nombre de archivo
refactor(repositorio): extraer lógica de consulta a Repository pattern
test(exportador): agregar tests de edge cases para lotes vacíos
docs(adr): registrar decisión de usar pytest sobre unittest
chore(deps): actualizar ruff a v0.5
```

### Tipos válidos
- `feat` — nueva funcionalidad
- `fix` — corrección de bug
- `refactor` — refactor sin cambio de comportamiento
- `test` — agregar o corregir tests
- `docs` — solo documentación
- `chore` — mantenimiento, deps, config
- `perf` — mejora de performance
- `ci` — cambios en CI/CD

### Breaking changes
```
feat!: cambiar API de exportador (BREAKING)

BREAKING CHANGE: el argumento `formato` ahora es `output_format`.
```

---

## Flujo completo de una feature

```bash
# 1. Crear worktree y rama
bash scripts/new-worktree.sh feat/mi-feature
cd ../ai-dev-starter-worktrees/feat-mi-feature

# 2. Abrir Claude Code y arrancar sesión
claude
# En Claude: /start-session

# 3. Ciclo TDD
# (RED) Escribir test que falla
# (GREEN) Implementación mínima
# (REFACTOR) Mejorar calidad

# 4. Commit (lefthook corre los checks automáticamente)
git add .
git commit -m "feat(modulo): descripción concreta"

# 5. Push y abrir PR
git push origin feat/mi-feature

# 6. Cerrar sesión
# En Claude: /end-session

# 7. Post-merge: limpiar
cd ../../ai-dev-starter
bash scripts/cleanup-worktrees.sh
```
