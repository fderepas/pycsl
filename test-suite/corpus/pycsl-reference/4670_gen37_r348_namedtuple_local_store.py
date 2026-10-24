r"""Test 4670 -- gen #37 route #348 (expected FAIL): witness j02: local NamedTuple `n = N(1); n.x = 7`; PROVED (CPython AttributeError). REFUSED (PYCSL-R348-IMMUTABLE-RECORD-STORE, route #348).
"""
# pycsl-expected: FAIL
from typing import NamedTuple

class N(NamedTuple):
    x: int

#@ no_exception \all
#@ ensures \result == 7
def f() -> int:
    n = N(1)
    n.x = 7
    return n.x

if __name__ == "__main__":
    print(f())
