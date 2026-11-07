r"""Test 3190 — route #282 VERIFIED-CALLER ALIAS CONTROL (expected FAIL): the callee of 3180 called from VERIFIED code as `f(a, a)`
(and `b = a; f(a, b)` in `g2`). `g` claims `\result == 1`; CPython returns 2. Fails closed: Why3 rejects
the application ("This application creates an illegal alias", L3-tc), so the PARAM-DISJOINT residue
is only an alias built in unverified code.
"""
# pycsl-expected: FAIL
from typing import List
#@ requires len(xs) == 1 and len(ys) == 1
#@ ensures ys[0] == \old(ys[0])
#@ assigns xs[0]
def f(xs: List[int], ys: List[int]) -> None:
    xs[0] = ys[0] + 1

#@ ensures \result == 1
def g() -> int:
    a = [1]
    f(a, a)
    return a[0]


#@ ensures \result == 1
def g2() -> int:
    a = [1]
    b = a
    f(a, b)
    return b[0]


if __name__ == "__main__":
    print(g())  # 2
    assert g() == 2 and g2() == 2
