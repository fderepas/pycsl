r"""Test 2975 — route #274 (expected FAIL): a VISIBLE `push(c)` before the comprehension
must not excuse the vanished ones: each application is one more write. `push` increments
`c.v`; `push(c); [push(c) for y in [1, 2]]` leaves `c.v == 3`, but only the visible call
was modelled and `\result == 1` PROVED at 5a307a33. CPython: 3. Now refused
(PYCSL-SEM-VANISHED-CALL-EFFECT).
"""
# pycsl-expected: FAIL

class C:
    def __init__(self) -> None:
        self.v: int = 0

#@ ensures \result == 1 and c.v == \old(c.v) + 1
#@ assigns c.v
def push(c: C) -> int:
    c.v = c.v + 1
    return 1

#@ requires c.v == 0
#@ ensures \result == 1
#@ assigns c.v
def f(c: C) -> int:
    push(c)
    ys = [push(c) for y in [1, 2]]
    return c.v

if __name__ == "__main__":
    print(f(C()))
