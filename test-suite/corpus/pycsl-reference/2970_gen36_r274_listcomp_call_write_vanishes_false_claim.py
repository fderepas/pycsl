r"""Test 2970 — route #274 (expected FAIL): `ys = [push(c) for y in xs]` runs
`push`, which declares `assigns c.v` and sets `c.v = 5`; the comprehension lowers to an opaque
`list_comp 0`, the write vanished, and `\result == 0` PROVED at 5a307a33. CPython: 5. Now refused (PYCSL-SEM-VANISHED-CALL-EFFECT).
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

#@ requires c.v == 0
#@ ensures \result == 0
#@ assigns c.v
def f(c: C) -> int:
    xs: List[int] = [1]
    ys = [push(c) for y in xs]
    return c.v

if __name__ == "__main__":
    print(f(C()))
