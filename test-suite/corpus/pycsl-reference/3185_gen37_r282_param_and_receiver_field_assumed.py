r"""Test 3185 — route #282 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION PARAM-DISJOINT).

`T.m(self, xs)` (`assigns xs[0]`) writes `xs[0] = 7` and returns `self.ys[0]` under `requires
self.ys[0] == 0`; `ensures \result == 0` PROVES: a list parameter and a list field of the receiver are
distinct regions. CPython returns 7 for `L = [0]; T(L).m(L)` (and for `t.m(t.ys)`). VERIFIED callers
building either alias fail closed: the constructor's stored list is havocked and the stubbed-method
precondition is `assert false` (R167, corpus 3195). `--soundness-report` lists PARAM-DISJOINT
(`t__m: writes through xs, also accesses self`). No strict mode.
"""
# pycsl-model-assumption: PARAM-DISJOINT
# pycsl-expected: PASS
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


if __name__ == "__main__":
    L = [0]
    t = T(L)
    print(t.m(L), T([0]).m([0]))  # 7 0: the claim is FALSE when xs is self.ys
    u = T([0])
    assert u.m(u.ys) == 7
