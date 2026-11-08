r"""Test 2972 — route #274 (expected FAIL): `sum(push(c) for y in xs)` consumes the
generator and runs `push(c)`; the opaque `sum` dropped the write. PROVED `\result == 0` at
5a307a33. CPython: 5. Now refused (PYCSL-SEM-VANISHED-CALL-EFFECT).
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
    s = sum(push(c) for y in xs)
    return c.v

if __name__ == "__main__":
    print(f(C()))
