# Suite de tests

## Estructura

```
tests/
├── unit/           # Tests unitarios puros (sin I/O, sin BD)
│   └── test_*.py
├── integration/    # Tests de integración (BD, APIs externas)
│   └── test_*.py
└── conftest.py     # Fixtures compartidas
```

## Convención de nombres

- Archivos: `test_[módulo_que_testea].py`
- Funciones: `test_[comportamiento_esperado]_when_[condición]()`

```python
# ✅ Correcto
def test_calcula_hash_correcto_when_operacion_valida():
    ...

def test_rechaza_parte_when_codigo_epec_invalido():
    ...

# ❌ Incorrecto
def test_hash():
    ...

def test_validacion():
    ...
```

## Markers

```python
@pytest.mark.unit        # Puro, sin I/O
@pytest.mark.integration # Toca BD o servicios externos
@pytest.mark.slow        # Tarda más de 1 segundo
```

## Correr tests

```bash
# Todos los tests unitarios (rápido)
uv run pytest tests/ -m "not integration" -v

# Tests de integración (requiere BD levantada)
uv run pytest tests/ -m integration -v

# Con cobertura
uv run pytest tests/ --cov=src --cov-report=term-missing

# Un test específico
uv run pytest tests/unit/test_mi_modulo.py::test_nombre_especifico -v
```

## TDD: el test siempre primero

Ver `.claude/skills/tdd-guide/SKILL.md` para el proceso completo.
El hook `PreToolUse` verifica que haya un test en RED antes de escribir implementación.
