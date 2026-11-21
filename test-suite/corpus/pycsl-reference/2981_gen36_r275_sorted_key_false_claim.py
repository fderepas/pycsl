r"""Test 2981 — route #275 (expected FAIL): `sorted(xs, key=lambda v: -v)` lowered to
`sorted_1 xs` (the key DROPPED) and PROVED ascending order. CPython: the key sorts
`[1, 2]` to `[2, 1]`, so f() is False. Now a `key` keeps only length + permutation.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    xs: List[int] = [1, 2]
    ys = sorted(xs, key=lambda v: -v)
    return ys[0] <= ys[1]


if __name__ == "__main__":
    assert f() is False
