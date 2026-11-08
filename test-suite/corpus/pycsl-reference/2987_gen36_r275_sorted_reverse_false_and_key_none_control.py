r"""Test 2987 — route #275 control (expected PASS): `reverse=False` and `key=None` are the
defaults, so the ascending model still applies and these TRUE claims prove.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    xs: List[int] = [2, 1]
    ys = sorted(xs, reverse=False)
    return ys[0] <= ys[1]


#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    xs: List[int] = [2, 1]
    ys = sorted(xs, key=None)
    return ys[0] <= ys[1]


if __name__ == "__main__":
    assert f() is True
    assert g() is True
