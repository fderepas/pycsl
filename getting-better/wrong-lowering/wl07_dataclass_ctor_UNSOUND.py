"""WL-07 — `@dataclass` positional constructor DROPPED its args — **FIXED**.

Before the fix (severity-1 UNSOUND, fail-OPEN): a `@dataclass` with NO explicit
`__init__` had its SYNTHESIZED constructor's args DROPPED — Module5's
`_collect_init_construction` only walked an EXPLICIT `__init__`, so a dataclass got
empty `init_params`/`init_body` and `_call_record_constructor` fell EVERY field back
to its zero default. So `Point(1, 2)` emitted `{ x = 0; y = 0 }` and this driver
PROVED `Point(1, 2).x == 0` — a green proof of a claim FALSE of real Python
(`Point(1, 2).x` is `1`). This is the FALSE-TWIN soundness oracle.

After the fix (wrong-lowering-to-fix.md §WL-07): the synthesized `@dataclass`
constructor binds each field from its same-position positional arg in
field-declaration order (`Point(1, 2)` -> `{ x = 1; y = 2 }`), so the false `== 0`
claim is UNPROVEN. Verdict: UNPROVEN (was PROVEN)."""
_ = 0
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


#@ ensures \result == 0
def dropped_arg_UNSOUND() -> int:
    """Claims Point(1, 2).x == 0 — the old field-default collapse. FALSE of Python."""
    p = Point(1, 2)
    return p.x
