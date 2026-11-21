r"""Test 2977 — route #274 (expected FAIL): `relay` declares NO `assigns` (its frame is
inferred) and calls `push`, which writes `c.v = 5`; `[relay(c) for y in xs]` hides both.
PROVED `\result == 0` at 5a307a33. CPython: 5. Now refused (PYCSL-SEM-VANISHED-CALL-EFFECT):
an undeclared frame is closed transitively over the callee's own calls.
"""
# pycsl-expected: FAIL
from typing import List

class C:
    def __init__(self) -> None:
        self.v: int = 0

#@ ensures \result == 1
#@ assigns c.v
def push(c: C) -> int:
    c.v = 5
    return 1

#@ ensures \result == 1
def relay(c: C) -> int:
    push(c)
    return 1

#@ requires c.v == 0
#@ ensures \result == 0
#@ assigns c.v
def f(c: C) -> int:
    xs: List[int] = [1]
    ys = [relay(c) for y in xs]
    return c.v

if __name__ == "__main__":
    print(f(C()))
