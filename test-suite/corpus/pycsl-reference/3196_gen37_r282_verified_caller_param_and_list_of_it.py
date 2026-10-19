r"""Test 3196 — route #282 VERIFIED-CALLER ALIAS CONTROL (expected FAIL): the callee of 3186 called from VERIFIED code as `f(r, [r])`.
`g` returns `m[0][0]` after `f(r, m)` with `m = [r]` and claims `\result == 0`; CPython returns 9. It
fails closed (ill-typed: the literal `[r]` is an `array (array int)`, the parameter takes an `array`
of `seq` element snapshots, L3-tc).
"""
# pycsl-expected: FAIL
from typing import List
#@ requires len(xs) == 1 and len(xss) == 1 and len(xss[0]) == 1
#@ ensures xss[0][0] == \old(xss[0][0])
#@ assigns xs[0]
def f(xs: List[int], xss: List[List[int]]) -> None:
    xs[0] = 9

#@ ensures \result == 0
def g() -> int:
    r = [0]
    m = [r]
    f(r, m)
    return m[0][0]


if __name__ == "__main__":
    print(g())  # 9
    assert g() == 9
