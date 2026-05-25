"""Find a `def` node inside a libcst Module by Python qualname.

The qualname is dot-separated and refers to nesting inside the module:

  - "foo"             → top-level function `foo`
  - "Bar.baz"         → method `baz` on class `Bar`
  - "outer.inner"     → nested function `inner` inside `outer`
  - "Bar.Inner.baz"   → arbitrary depth

The module prefix (`pycsl.parser.parse_expression` → strip `pycsl.parser.`)
is the caller's responsibility. The locator works on a single parsed
module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import libcst as cst


@dataclass(frozen=True)
class FunctionMatch:
    """Locator result.

    `parent_body` is the `IndentedBlock` (or `Module`) that *contains*
    the matched `def`, so the annotator can rebuild it with a replaced
    function node. `index` is the position of the match inside that
    body's `body` tuple.
    """
    parent_body: cst.IndentedBlock | cst.Module
    index: int
    node: cst.FunctionDef


def find_function(module: cst.Module, qualname: str) -> Optional[FunctionMatch]:
    """Locate `qualname` inside `module`.

    Returns None if no such function is found. Returns the *first* match
    if duplicates exist at the same qualname (which would be invalid
    Python anyway).
    """
    parts = qualname.split(".")
    if not parts or any(not p for p in parts):
        raise ValueError(f"invalid qualname: {qualname!r}")

    return _descend(module, module.body, parts)


def _descend(
    parent: cst.IndentedBlock | cst.Module,
    statements: tuple,
    parts: list[str],
) -> Optional[FunctionMatch]:
    """Walk `statements` looking for the head of `parts`.

    `parent` is what we return as `parent_body` if we match at this level.
    `statements` is `parent.body` already destructured (so we can recurse
    into class/function bodies that also expose `.body`).
    """
    if not parts:
        return None
    head, *rest = parts

    for index, stmt in enumerate(statements):
        # libcst wraps top-level statements in SimpleStatementLine /
        # FunctionDef / ClassDef. We care about the latter two.
        if isinstance(stmt, cst.FunctionDef) and stmt.name.value == head:
            if not rest:
                return FunctionMatch(parent_body=parent, index=index, node=stmt)
            # Nested def — recurse into the function body
            inner = _descend(stmt.body, stmt.body.body, rest)
            if inner is not None:
                return inner
        elif isinstance(stmt, cst.ClassDef) and stmt.name.value == head:
            # Class qualname — recurse into the class body for the remainder
            inner = _descend(stmt.body, stmt.body.body, rest) if rest else None
            if inner is not None:
                return inner
    return None
