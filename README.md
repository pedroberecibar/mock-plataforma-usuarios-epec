# AI Dev Starter

Base para proyectos con workflow IA estandarizado. Cloná, instalá y trabajás — las reglas se aplican solas.

> **Agnóstico de stack.** Las reglas de TDD, arquitectura y seguridad son universales. El stack concreto (lenguaje, framework, test runner) se define en `CLAUDE.md` al iniciar cada proyecto.

**Requisitos:** Claude Code · Git 2.35+ · Lefthook · Node.js LTS (para commitlint/npx) · [tools del stack elegido]

---

## Instalación (una vez por máquina)

```bash
git clone https://github.com/[org]/ai-dev-starter.git mi-proyecto
cd mi-proyecto
bash scripts/setup.sh          # instala hooks, crea .env, configura vault
# Editá .env: completá VAULT_PATH y las variables del stack elegido
# Editá CLAUDE.md: completá la sección ## Stack con tu lenguaje, framework y test runner
```

---

## Flujo diario

```bash
claude                         # ← única acción para empezar el día
                               # Claude lee automáticamente el contexto del día anterior
                               # y te dice en qué estabas
```

Después, **solo chateás** con Claude. Él aplica las reglas solo:

| Mientras trabajás | Automático |
|-------------------|------------|
| Test antes de implementar (TDD Red→Green→Refactor) | ✅ Hook en cada edición de `src/` |
| Reglas de arquitectura, seguridad y estilo | ✅ `CLAUDE.md` siempre en contexto |
| Linters, type check, secrets scan | ✅ En cada `git commit` (Lefthook) |
| Tests + arch + security scan completo | ✅ En cada `git push` (GitHub Actions) |
| Guardar decisiones técnicas en el vault | ✅ Hook PostToolUse automático |
| Guardar el estado al cerrar | ✅ Decís "terminamos" y Claude actualiza `CONTEXT.md` |

**Los únicos 3 comandos manuales que existen:**

```bash
bash scripts/new-worktree.sh feat/nombre   # nueva feature en worktree aislado
claude --agent code-reviewer               # revisar PR antes de mergear (siempre)
claude --agent security-reviewer           # si el PR toca auth, SQL o archivos
```

---

## Commits

Formato obligatorio (enforced por commitlint):
```
feat(módulo): descripción    fix(módulo): descripción    refactor · docs · chore · test
```

---

## Qué hay en el repo

| Qué | Dónde |
|-----|-------|
| Reglas permanentes para Claude (TDD, arquitectura, seguridad, git) | `CLAUDE.md` |
| Conocimiento acumulado del proyecto (crece con el tiempo) | `MEMORY.md` |
| Estado de la última sesión (qué quedó, qué hacer hoy) | `CONTEXT.md` |
| Skills de Claude: sesión, TDD, patrones, BDD, diseño UI | `.claude/skills/` |
| Agentes: code-reviewer, security-reviewer, ui-designer, docs-updater | `.claude/agents/` |
| Fitness functions de Clean Architecture (se corren en CI) | `architecture/tests/` |
| Template ADR para registrar decisiones técnicas | `architecture/adr/` |
| Setup, worktrees, cleanup, captura de decisiones | `scripts/` |
| Onboarding, git workflow, roles de agentes | `docs/` |

---

## Troubleshooting rápido

| Problema | Solución |
|----------|----------|
| Hooks no corren | `lefthook install` |
| Serena no indexa | Cerrar Ollama/Twinny, reiniciar Claude Code |
| `uv sync` falla | `python -m venv .venv` → `pip install -e ".[dev]"` |
| Proxy bloquea descargas | El núcleo corre offline; pedir binario al equipo |
| Sesión muy larga / contexto lleno | `/compact` → si sigue: "terminamos" → nueva sesión |
