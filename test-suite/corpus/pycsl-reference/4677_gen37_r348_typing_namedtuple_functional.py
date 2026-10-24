r"""Test 4677 -- gen #37 route #348 (expected FAIL): (new) functional `NamedTuple("P", [...])` store; PROVED (CPython AttributeError). REFUSED (PYCSL-R348-IMMUTABLE-RECORD-STORE, route #348).
"""
# pycsl-expected: FAIL
from typing import NamedTuple
P = NamedTuple("P", [("x", int), ("y", int)])

#@ no_exception \all
def f(p: P) -> int:
    p.x = 5
    return 5

if __name__ == "__main__":
    print(f(P(1, 2)))
