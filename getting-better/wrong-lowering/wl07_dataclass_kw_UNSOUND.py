"""WL-07 (keyword arm) — keyword `@dataclass` construction DROPPED its args —
**FIXED**.

Before the fix (severity-1 UNSOUND, fail-OPEN — a pre-existing hole affecting ALL
record constructors, plain classes too): EXPLICIT keyword arguments were DROPPED
from the Call IR entirely (`_py_expr_call` recorded only `expr.args`), so
`Point(x=1, y=2)` became `Call(args=[])` and every field fell to its zero default —
this driver PROVED `Point(x=1, y=2).x == 0`, FALSE of real Python.

After the fix (wrong-lowering-to-fix.md §WL-07): keyword args are captured in the
Call IR (`CallExpr.keywords`) and bound BY NAME in `_call_record_constructor`, so
`Point(x=1, y=2)` -> `{ x = 1; y = 2 }` and the false `== 0` claim is UNPROVEN.
Verdict: UNPROVEN (was PROVEN)."""
_ = 0
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


#@ ensures \result == 0
def kw_dropped_arg_UNSOUND() -> int:
    """Claims Point(x=1, y=2).x == 0 — the old keyword-drop collapse. FALSE."""
    p = Point(x=1, y=2)
    return p.x
