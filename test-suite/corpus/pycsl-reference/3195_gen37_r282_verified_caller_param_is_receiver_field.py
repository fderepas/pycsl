r"""Test 3195 — route #282 VERIFIED-CALLER ALIAS CONTROL (expected FAIL): the method of 3185 called
from VERIFIED code with `xs` = the receiver's `ys`: `T(L).m(L)` (`g`), `t.m(t.ys)` (`g2`), and with a
parameter stored then passed (`g3`). Each claims `\result == 0`; CPython returns 7. Fails closed: the
constructor's stored list is havocked (`any_array ()`) and the stubbed-method precondition is
`assert false` (R167).
"""
# pycsl-expected: FAIL
from typing import List
class T:
    def __init__(self, ys: List[int]) -> None:
        self.ys: List[int] = ys

    #@ requires len(xs) == 1 and \length(self.ys) == 1 and self.ys[0] == 0
    #@ ensures \result == 0
    #@ assigns xs[0]
    def m(self, xs: List[int]) -> int:
        xs[0] = 7
        return self.ys[0]

#@ ensures \result == 0
def g() -> int:
    L = [0]
    t = T(L)
    return t.m(L)


#@ ensures \result == 0
def g2() -> int:
    t = T([0])
    return t.m(t.ys)


#@ requires len(L) == 1 and L[0] == 0
#@ ensures \result == 0
def g3(L: List[int]) -> int:
    t = T(L)
    return t.m(L)


if __name__ == "__main__":
    print(g(), g2(), g3([0]))  # 7 7 7
    assert g() == 7 and g2() == 7 and g3([0]) == 7
