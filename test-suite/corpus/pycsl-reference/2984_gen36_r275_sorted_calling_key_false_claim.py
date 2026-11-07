r"""Test 2984 — route #275 (expected FAIL): a `key` that CALLS something (`lambda v: -abs(v)`)
was dropped and the ascending model PROVED `ys[0] <= ys[1]`. CPython: `[2, 1]`, f() is False.
A key whose body makes a call is refused (its effects/raises are not modelled).
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    xs: List[int] = [1, 2]
    ys = sorted(xs, key=lambda v: -abs(v))
    return ys[0] <= ys[1]


if __name__ == "__main__":
    assert f() is False
