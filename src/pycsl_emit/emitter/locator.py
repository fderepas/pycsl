"""Find a `def` node inside a parsed module by Python qualname.

The qualname is dot-separated and refers to nesting inside the module:

  - "foo"             → top-level function `foo`
  - "Bar.baz"         → method `baz` on class `Bar`
  - "outer.inner"     → nested function `inner` inside `outer`
  - "Bar.Inner.baz"   → arbitrary depth

The module prefix (`pycsl.parser.parse_expression` → strip `pycsl.parser.`)
is the caller's responsibility. The locator works on a single parsed
module (a `pure_ast` tree — the pure-Python front-end, no libcst).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:                                  # verify-pipeline / tests: src/pycsl on sys.path
    import pure_ast as ast  # noqa: F401
except ModuleNotFoundError:           # installed console scripts (rocq2pycsl, …)
    from pycsl import pure_ast as ast  # noqa: F401


@dataclass(frozen=True)
class FunctionMatch:
    """Locator result: the matched `def`/`async def` node (a `pure_ast`
    FunctionDef/AsyncFunctionDef). Its `.lineno` / `.col_offset` /
    `.decorator_list` drive position-based annotation insertion."""
    node: object


def find_function(module, qualname: str) -> Optional[FunctionMatch]:
    """Locate `qualname` inside `module` (a `pure_ast.parse` result).

    Returns None if not found; the first match if duplicates exist at the
    same qualname (invalid Python anyway)."""
    parts = qualname.split(".")
    if not parts or any(not p for p in parts):
        raise ValueError(f"invalid qualname: {qualname!r}")
    return _descend(module.body, parts)


def _descend(statements, parts):
    head, *rest = parts
    for stmt in statements:
        t = type(stmt).__name__
        if t in ("FunctionDef", "AsyncFunctionDef") and stmt.name == head:
            if not rest:
                return FunctionMatch(node=stmt)
            inner = _descend(stmt.body, rest)   # nested def
            if inner is not None:
                return inner
        elif t == "ClassDef" and stmt.name == head and rest:
            inner = _descend(stmt.body, rest)   # recurse into class body
            if inner is not None:
                return inner
    return None
