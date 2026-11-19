r"""Test 4673 -- gen #37 route #348 (expected FAIL): (new) `n.x += 1` on a NamedTuple; PROVED (CPython AttributeError). REFUSED (PYCSL-R348-IMMUTABLE-RECORD-STORE, route #348).
"""
# pycsl-expected: FAIL
from typing import NamedTuple

class N(NamedTuple):
    x: int

#@ no_exception \all
#@ ensures \result == 2
def f() -> int:
    n = N(1)
    n.x += 1
    return n.x

if __name__ == "__main__":
    print(f())
