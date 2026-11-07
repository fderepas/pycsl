r"""Test 2980 — route #275 (expected FAIL): `sorted(xs, reverse=True)` lowered to `sorted_1 xs`
(the keyword DROPPED), whose `ensures` says ASCENDING, so `ys[0] <= ys[1]` PROVED. CPython:
`sorted([1, 2], reverse=True) == [2, 1]`, so f() is False. Now `reverse=True` is DESCENDING.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    xs: List[int] = [1, 2]
    ys = sorted(xs, reverse=True)
    return ys[0] <= ys[1]


if __name__ == "__main__":
    assert f() is False
