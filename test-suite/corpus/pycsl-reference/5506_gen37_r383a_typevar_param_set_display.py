r"""Test 5506 -- gen #37 route #383 allow-list addendum (expected FAIL): `d: T` (a TypeVar) hashed by `{d}`, called with a list (CPython TypeError; PROVED at base b62ff2e23). REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
from typing import TypeVar

T = TypeVar("T")

#@ no_exception \all
#@ ensures \result == 1
def g(d: T) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g([1]))
