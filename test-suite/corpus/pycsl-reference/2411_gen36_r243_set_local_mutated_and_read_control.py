r"""Test 2311 — gen #36 r243 (expected PASS): routes #243/#244 CONTROL: a set LOCAL mutated and read back keeps proving (CPython: True).
"""
# pycsl-expected: PASS
from typing import Set


#@ ensures \result == True
def f() -> bool:
    s: Set[int] = set()
    s.add(1)
    return 1 in s


if __name__ == "__main__":
    assert f() is True
