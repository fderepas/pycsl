r"""Test 4754 -- gen #37 route #353 (expected FAIL): mixin `__eq__` without `__hash__` sets `__hash__ = None`: `hash(x)` under `no_exception \all` PROVED (CPython TypeError). REFUSED now (route #353).
"""
# pycsl-expected: FAIL
from enum import Enum

class M:
    def __eq__(self, o: object) -> bool:
        return self is o

class C(M, Enum):
    A = 1

#@ no_exception \all
def f() -> int:
    x = C.A
    return hash(x)

if __name__ == "__main__":
    f()
