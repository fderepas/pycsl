r"""Test 4772 -- gen #37 route #353 (expected PASS): CONTROL: `class C(int, Enum)` (MRO int, Enum only) keeps int semantics: `x - x == 0` proves (CPython 0).
"""
# pycsl-expected: PASS
from enum import Enum

class C(int, Enum):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.A
    return x - x

if __name__ == "__main__":
    assert f() == 0
