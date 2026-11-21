r"""Test 2985 — route #275 coverage (expected PASS; FAILED at 5a307a33, which modelled it ascending): `sorted(xs, reverse=True)` IS descending, and
that TRUE claim proves. CPython: `sorted([1, 2], reverse=True) == [2, 1]`.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    xs: List[int] = [1, 2]
    ys = sorted(xs, reverse=True)
    return ys[0] >= ys[1]


if __name__ == "__main__":
    assert f() is True
