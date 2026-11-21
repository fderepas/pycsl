r"""Test 2713 — route #262 (expected FAIL): a quantifier binder is a symbolic index too —
`\forall i; i == -1 ==> xs[i] == \old(xs[i])` read raw cell `-1` and PROVED at b35d9c5e.
CPython: for i = -1, xs[-1] goes 0 -> 7.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires len(xs) == 2
#@ requires xs[1] == 0
#@ ensures \forall i; i == -1 ==> xs[i] == \old(xs[i])
#@ assigns xs[1]
def f(xs: List[int]) -> None:
    xs[1] = 7


if __name__ == "__main__":
    xs = [0, 0]
    f(xs)
    assert xs[-1] == 7
