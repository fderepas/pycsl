r"""Test 3182 — route #282 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION PARAM-DISJOINT).

`f(xss)` (`assigns xss[0][0]`) writes `xss[0][0] = 9`; `ensures xss[1][0] == \old(xss[1][0])` PROVES:
a `List[List[int]]` is an array of independent element values. CPython violates it for `r = [0];
f([r, r])` — ONE list twice. A VERIFIED caller building `[r, r]` (or `m.append(r)` twice) gets an
`array (array int)` the `matrix` parameter rejects (ill-typed, fail-closed, corpus 3192).
`--soundness-report` lists PARAM-DISJOINT (`f: writes an element of xss ...`). No strict mode.
"""
# pycsl-model-assumption: PARAM-DISJOINT
# pycsl-expected: PASS
from typing import List


#@ requires len(xss) == 2 and len(xss[0]) == 1 and len(xss[1]) == 1
#@ ensures xss[1][0] == \old(xss[1][0])
#@ assigns xss[0][0]
def f(xss: List[List[int]]) -> None:
    xss[0][0] = 9


if __name__ == "__main__":
    r = [0]
    m = [r, r]
    f(m)
    print(m)  # [[9], [9]]: xss[1][0] changed from 0 to 9
    assert m[1][0] == 9
