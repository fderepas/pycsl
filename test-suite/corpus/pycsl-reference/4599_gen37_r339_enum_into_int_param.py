r"""Test 4599 -- gen #37 route #339 (expected FAIL): NEW latent shape (r339 executor): a plain `Enum` member passed to an `int` parameter, the callee computing `v - v` under `no_exception \all`: PROVED (CPython TypeError). REFUSED now (PYCSL-SEM-ENUM-MEMBER-OPERATION, route #339).
"""
# pycsl-expected: FAIL
from enum import Enum

class C(Enum):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def h(v: int) -> int:
    return v - v

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    return h(C.A)

if __name__ == "__main__":
    assert f() == 0
