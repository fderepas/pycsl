r"""Test 5344 -- gen #37 route #382 (expected FAIL): `d: deque`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from collections import deque

#@ no_exception \all
#@ ensures \result == 1
def g(d: deque) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(deque()))
