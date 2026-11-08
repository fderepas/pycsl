r"""Test 2305 — gen #36 r243 (expected FAIL): route #243: a local alias of a dict PARAMETER (`e = d`) stored through. Route #59's guard
only knew dict LOCALS. CPython returns True; PROVED at cdac19a6, now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == False
def f(d: Dict[int, int]) -> bool:
    if 1 in d:
        return False
    e = d
    e[1] = 5
    return 1 in d


if __name__ == "__main__":
    assert f({}) is True
