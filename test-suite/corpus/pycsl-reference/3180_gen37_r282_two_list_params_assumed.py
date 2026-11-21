r"""Test 3180 — route #282 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION PARAM-DISJOINT).

`f(xs, ys)` (`assigns xs[0]`) writes `xs[0] = ys[0] + 1`; `ensures ys[0] == \old(ys[0])` PROVES: each
list parameter is its own Why3 region, so the write through `xs` is invisible through `ys`. CPython
violates it for `a = [1]; f(a, a)` (see `__main__`). A VERIFIED caller that builds that alias fails
closed (Why3 "illegal alias", corpus 3190); the residue is an alias built in unverified code, the
ownership discipline's rule R1. `pycsl --soundness-report` lists PARAM-DISJOINT for this file
(`f: writes through xs, also accesses ys`). No strict mode.
"""
# pycsl-model-assumption: PARAM-DISJOINT
# pycsl-expected: PASS
from typing import List


#@ requires len(xs) == 1 and len(ys) == 1
#@ ensures ys[0] == \old(ys[0])
#@ assigns xs[0]
def f(xs: List[int], ys: List[int]) -> None:
    xs[0] = ys[0] + 1


if __name__ == "__main__":
    a = [1]
    f(a, a)
    print(a)  # [2]: ys[0] changed from 1 to 2 — the claim is FALSE for the aliased call
    assert a[0] == 2
