r"""Test 2343 — route #247 (expected FAIL): the route #246 identity key compares the parameter's tag
with the CLASS's tag literal, and `set`/`frozenset` had one literal (4): the two tests were one term,
so "a set that is not a frozenset" was unreachable and `\result == 1` PROVED at afe28c69. CPython
`f({1})` = 0.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    a = 0
    if isinstance(x, set):
        a = 1
    b = 0
    if isinstance(x, frozenset):
        b = 1
    if a == 1 and b == 0:
        return 0
    return 1


if __name__ == "__main__":
    assert f({1}) == 0
