r"""Test 4669 -- gen #37 route #348 (expected FAIL): witness d11: NamedTuple parameter `n.x = 5`; PROVED (CPython AttributeError). REFUSED (PYCSL-R348-IMMUTABLE-RECORD-STORE, route #348).
"""
# pycsl-expected: FAIL
from typing import NamedTuple

class N(NamedTuple):
    x: int
    y: int

#@ no_exception \all
#@ ensures \result == 5
def f(n: N) -> int:
    n.x = 5
    return n.x

if __name__ == "__main__":
    print(f(N(1, 2)))
