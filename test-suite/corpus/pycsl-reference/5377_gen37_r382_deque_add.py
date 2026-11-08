r"""Test 5377 -- gen #37 route #382 (expected FAIL): NEW shape: `d: deque`, `s.add(d)` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from collections import deque

#@ no_exception \all
#@ ensures \result == 1
def g(d: deque) -> int:
    s: set = set()
    s.add(d)
    return 1

if __name__ == "__main__":
    print(g(deque()))
