r"""Test 3188 — route #282 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION PARAM-DISJOINT).

`h(p, q)` forwards its two list parameters to `f(xs, ys)` (`assigns xs[0]`, `ensures ys[0] ==
\old(ys[0])`) and returns `q[0]` under `requires q[0] == 0`; `ensures \result == 0` PROVES. The call
`f(p, q)` is accepted because `p` and `q` are distinct parameters — which is the assumption again, one
frame up: CPython returns 1 for `a = [0]; h(a, a)`. `--soundness-report` lists PARAM-DISJOINT for BOTH
`f` and `h` (the forwarding caller relies on it too). No strict mode.
"""
# pycsl-model-assumption: PARAM-DISJOINT
# pycsl-expected: PASS
from typing import List


#@ requires len(xs) == 1 and len(ys) == 1
#@ ensures ys[0] == \old(ys[0])
#@ assigns xs[0]
def f(xs: List[int], ys: List[int]) -> None:
    xs[0] = ys[0] + 1


#@ requires len(p) == 1 and len(q) == 1 and q[0] == 0
#@ ensures \result == 0
#@ assigns p[0]
def h(p: List[int], q: List[int]) -> int:
    f(p, q)
    return q[0]


if __name__ == "__main__":
    a = [0]
    print(h(a, a), h([0], [0]))  # 1 0: the claim is FALSE for the aliased call
    assert h([0], [0]) == 0
