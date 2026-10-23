r"""Test 1305 — ROUTE #111 negative witness: a dict-typed self-field store whose RHS is a
FIELD READ (`self.b = self.a`) was replaced by the EVERYWHERE-EMPTY MAP.

FALSE OF THE PROGRAM: `self.b = self.a` makes `1 in self.b` exactly `1 in self.a`; `f()`
constructs `a = {1: 5}`, so CPython returns 1 — and a method that only knows nothing about
`self.a` cannot prove `\result == 0` either.

At the parent commit this PROVED (rc=0): `statements.py` decided "keep this RHS?" with a
prefix test plus `str.isalnum()` over the LOWERED TEXT, and `self.a` is not alphanumeric, so
the store was emitted `self.b <- (const (None: option int))`. The same store routed through
a local (`!t` IS alphanumeric) survived. The repair asks the RHS IR (`_rhs_yields_map`) and
keeps a map-valued RHS; anything else becomes the unconstrained `any_map`, never the empty
map. Faithful twin: 1306. Call-valued spelling: 1307.
"""
# pycsl-expected: FAIL
from typing import Dict

class C:
    a: Dict[int, int]
    b: Dict[int, int]
    #@ assigns self.a, self.b
    def __init__(self) -> None:
        self.a = {1: 5}
        self.b = {}

    #@ ensures \result == 0
    #@ assigns self.b
    def copy_and_check(self) -> int:
        self.b = self.a
        if 1 in self.b:
            return 1
        return 0


def f() -> int:
    c = C()
    return c.copy_and_check()
