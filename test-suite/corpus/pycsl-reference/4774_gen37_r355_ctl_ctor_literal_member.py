r"""Test 4774 -- gen #37 route #355 (expected PASS): CONTROL: `C(1)`, `C("b")`, `P(1)` with literal member values under `no_exception \all` prove (CPython ok).
"""
# pycsl-expected: PASS
from enum import Enum, IntEnum

class C(Enum):
    A = 1
    B = "b"

class P(IntEnum):
    LOW = 1

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(1)
    y = C("b")
    w = P(1)
    return 0

if __name__ == "__main__":
    assert f() == 0
