r"""Test 3192 — route #282 VERIFIED-CALLER ALIAS CONTROL (expected FAIL): the callee of 3182 called from VERIFIED code as `f([r, r])`.
`g` claims `\result == 0`; CPython returns 9. Fails closed: the literal `[r, r]` is an `array (array int)`
and the `List[List[int]]` parameter a `matrix` (ill-typed, L3-tc).
"""
# pycsl-expected: FAIL
from typing import List
#@ requires len(xss) == 2 and len(xss[0]) == 1 and len(xss[1]) == 1
#@ ensures xss[1][0] == \old(xss[1][0])
#@ assigns xss[0][0]
def f(xss: List[List[int]]) -> None:
    xss[0][0] = 9

#@ ensures \result == 0
def g() -> int:
    r = [0]
    m = [r, r]
    f(m)
    return m[1][0]


if __name__ == "__main__":
    print(g())  # 9
    assert g() == 9
