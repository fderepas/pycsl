r"""Test 5503 -- gen #37 route #383 allow-list addendum (expected FAIL): `d: Any` hashed by `s.add(d)`, called with a dict (CPython TypeError; PROVED at base b62ff2e23). REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
from typing import Any, Set

#@ no_exception \all
#@ ensures \result == 1
def g(d: Any) -> int:
    s: Set[int] = set()
    s.add(d)
    return 1

if __name__ == "__main__":
    print(g({1: 2}))
