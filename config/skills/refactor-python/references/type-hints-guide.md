---
name: refactor-python-type-hints
description: Systematic guide to adding type hints to existing Python code. Covers Python version compatibility, annotation order, typing imports, common patterns for Any/Optional/Union, and mypy/pyright integration. Use when Section 4 of the main skill applies.
---

# Type Hints Guide for Refactoring

---

## File setup

Every file that gains type hints must start with:

```python
from __future__ import annotations  # must be the very first non-docstring import
```

This enables:
- Forward references (class refers to itself in its own body)
- `list[str]`, `dict[str, Any]` syntax even on Python 3.8–3.9

Then import typing helpers appropriate to your Python version:

```python
# Python 3.8 / 3.9 (use capitalised names from typing)
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

# Python 3.10+ (lowercase builtins work directly; | for union)
# list[str], dict[str, Any], str | None, tuple[int, ...] all work natively
```

---

## Annotation order

Add annotations in this order to minimise disruption to reviewers:

1. **`__init__` return type** — always `-> None`. mypy warns without it; it's the most mechanical change.
2. **Public class methods** — `process()`, `generate()`, `run()`.
3. **Public module-level functions** — functions without a leading `_`.
4. **Private helpers** — `_build_prompt()`, `_validate()`, `_extract()`.
5. **Class attributes** — in `__init__` body: `self.x: Dict[str, str] = {}`.

---

## Common annotation patterns

### Basic types
```python
def greet(name: str) -> str: ...
def count(items: List[str]) -> int: ...
def maybe(x: Optional[str]) -> bool: ...  # Optional[X] == Union[X, None]
```

### Returning multiple things
```python
# Use Tuple for fixed-length heterogeneous returns
def split(text: str) -> Tuple[str, str]: ...

# Use Iterator for generators
def lines(path: str) -> Iterator[str]:
    with open(path) as f:
        yield from f
```

### Dicts and nested structures
```python
def load_config(path: str) -> Dict[str, Any]: ...
def get_functions(ir: Dict[str, Any]) -> List[Dict[str, Any]]: ...
```

### Optional with default
```python
# Wrong: Optional means None is a valid value, not "has a default"
# But in practice both are common
def process(items: List[str], limit: Optional[int] = None) -> str: ...
```

### Unknown or duck-typed params
```python
# Use Any with a comment explaining what's expected
def emit(node: Any) -> str:  # node: dict from JSON IR or CSL AST dataclass
    ...
```

### Callables
```python
from typing import Callable

def apply(transform: Callable[[str], str], code: str) -> str:
    return transform(code)

# With multiple args
def register(handler: Callable[[str, int], bool]) -> None: ...
```

### `*args` and `**kwargs`
```python
def log(*args: str) -> None: ...
def build(**kwargs: Any) -> Dict[str, Any]: ...
```

### `-> NoReturn` for functions that always raise
```python
from typing import NoReturn

def die(msg: str) -> NoReturn:
    raise RuntimeError(msg)
```

---

## `__init__` patterns

```python
class Parser:
    def __init__(self, grammar: str, strict: bool = True) -> None:
        self.grammar = grammar
        self.strict = strict
        # Annotate complex attributes here
        self._cache: Dict[str, Any] = {}
        self._errors: List[str] = []
```

---

## Python version compatibility table

| Type | Python 3.8–3.9 | Python 3.10+ |
|------|----------------|--------------|
| List | `List[str]` | `list[str]` |
| Dict | `Dict[str, int]` | `dict[str, int]` |
| Optional | `Optional[str]` | `str \| None` |
| Union | `Union[str, int]` | `str \| int` |
| Tuple fixed | `Tuple[int, str]` | `tuple[int, str]` |
| Tuple variadic | `Tuple[int, ...]` | `tuple[int, ...]` |
| Set | `Set[str]` | `set[str]` |
| Callable | `Callable[[str], int]` | `Callable[[str], int]` (unchanged) |

With `from __future__ import annotations`, Python 3.8–3.9 files can safely write `list[str]` in annotations — it's treated as a string at runtime and never evaluated. However, for maximum clarity and static analysis compatibility, prefer the `typing` forms in 3.8/3.9.

---

## When to use `Any`

Use `Any` when:
- The parameter accepts objects of multiple unrelated types (e.g., walking a JSON IR that can be `dict`, `list`, `str`, `int`).
- The type comes from an external library without stubs.
- A protocol or structural type would be correct but adds too much complexity for now.

Always add a comment explaining what values are actually expected:
```python
def collect_calls(obj: Any) -> Set[str]:  # obj: dict | list | str | int from JSON IR
    ...
```

---

## Mypy / pyright quick-start

```bash
# Install
pip install mypy

# Check a single file
mypy src/pycsl/Module1_Ingestor.py

# Check the whole package, ignore missing stubs for third-party libs
mypy src/pycsl/ --ignore-missing-imports

# Strict mode (catches more, but noisy on legacy code)
mypy src/pycsl/ --strict
```

Common suppressions (use sparingly):
```python
result: Any = some_library_call()  # type: ignore[return-value]
```

---

## Annotation checklist

Before marking type hint work complete on a file:

- [ ] `from __future__ import annotations` is the first import
- [ ] All `__init__` methods have `-> None`
- [ ] All public functions have param types and return types
- [ ] `Optional` used for params that can be `None`
- [ ] `Any` is annotated with a comment where used
- [ ] No bare `dict`, `list`, `tuple`, `set` in annotations (Python < 3.10)
- [ ] `python3 -m py_compile <file>` passes
- [ ] `mypy <file> --ignore-missing-imports` has no new errors
