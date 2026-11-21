r"""Test 4920 -- gen #37 route #366 (expected FAIL): NamedTuple with an `Any` field holding a dict; `hash(n)` (CPython TypeError). REFUSED now (route #366).
"""
# pycsl-expected: FAIL
from typing import Any, NamedTuple

class N(NamedTuple):
    v: Any

#@ no_exception \all
#@ ensures \result == 1
def g(n: N) -> int:
    h = hash(n)
    return 1

if __name__ == "__main__":
    print(g(N({})))
