r"""Test 3186 — route #282 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION PARAM-DISJOINT).

`f(xs, xss)` (`assigns xs[0]`) writes `xs[0] = 9`; `ensures xss[0][0] == \old(xss[0][0])` PROVES: a list
parameter and an element of a `List[List[int]]` parameter are distinct values. CPython violates it
for `r = [0]; f(r, [r])`. A VERIFIED `f(r, [r])` is ill-typed (fail-closed, corpus 3196).
`--soundness-report` lists PARAM-DISJOINT (`f: writes through xs, also accesses xss`). No strict mode.
"""
# pycsl-model-assumption: PARAM-DISJOINT
# pycsl-expected: PASS
from typing import List


#@ requires len(xs) == 1 and len(xss) == 1 and len(xss[0]) == 1
#@ ensures xss[0][0] == \old(xss[0][0])
#@ assigns xs[0]
def f(xs: List[int], xss: List[List[int]]) -> None:
    xs[0] = 9


if __name__ == "__main__":
    r = [0]
    m = [r]
    f(r, m)
    print(m)  # [[9]]: xss[0][0] changed from 0 to 9
    assert m[0][0] == 9
