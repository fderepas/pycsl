r"""Test 2971 — route #274 (expected FAIL): a generator expression evaluates
its FIRST iterable eagerly: `(y for y in range(push(c)))` runs `push(c)` (`c.v = 5`) at
creation even if never consumed. PROVED `\result == 0` at 5a307a33. CPython: 5. Now refused (PYCSL-SEM-VANISHED-CALL-EFFECT).
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
    g = (y for y in range(push(c)))
    return c.v

if __name__ == "__main__":
    print(f(C()))
