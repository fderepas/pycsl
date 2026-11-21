r"""Test 2719 — route #262 CONTROL (expected PASS): a quantified frame guarded by
`0 <= i` — the binder's normalisation is the identity under the guard; the TRUE claim proves.
"""
from typing import List


#@ requires len(xs) == 3
#@ ensures \forall i; 0 <= i and i < 2 ==> xs[i] == \old(xs[i])
#@ assigns xs[2]
def f(xs: List[int]) -> None:
    xs[2] = 7


if __name__ == "__main__":
    xs = [1, 2, 0]
    f(xs)
    assert xs == [1, 2, 7]
