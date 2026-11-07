r"""Test 1306 — ROUTE #111 faithful twin: a dict-typed self-field store from a FIELD READ
now carries the value.

TRUE OF THE PROGRAM: `t = {1: 5}; self.a = t; self.b = self.a` puts key 1 in `self.b`, so
the method returns 1. At the parent commit this was REFUSED — `self.b <- self.a` was emitted
as `self.b <- (const (None: option int))` — so the repair is FAITHFUL, not merely refusing:
the emitted store is now `self.b <- self.a` and the true claim PROVES. Negative: 1305.
"""
from typing import Dict

class C:
    a: Dict[int, int]
    b: Dict[int, int]
    #@ assigns self.a, self.b
    def __init__(self) -> None:
        self.a = {}
        self.b = {}

    #@ ensures \result == 1
    #@ assigns self.a, self.b
    def copy_and_check(self) -> int:
        t: Dict[int, int] = {1: 5}
        self.a = t
        self.b = self.a
        if 1 in self.b:
            return 1
        return 0


def f() -> int:
    c = C()
    return c.copy_and_check()
