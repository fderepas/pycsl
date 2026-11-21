r"""Test 4672 -- gen #37 route #348 (expected FAIL): witness j07: `collections.namedtuple` store; PROVED (CPython AttributeError). REFUSED (PYCSL-R348-IMMUTABLE-RECORD-STORE, route #348).
"""
# pycsl-expected: FAIL
from collections import namedtuple
P = namedtuple("P", ["x", "y"])

#@ no_exception \all
#@ ensures \result == 5
def f(p: P) -> int:
    p.x = 5
    return 5

if __name__ == "__main__":
    print(f(P(1, 2)))
