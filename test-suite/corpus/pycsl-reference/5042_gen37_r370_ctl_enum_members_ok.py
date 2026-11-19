r"""Test 5042 -- gen #37 route #370 (expected PASS): CONTROL: `_ignore_` literal, a member alias, a `def`; `C(2)`, `C.C2`, `C.A.value` (CPython ok).
"""
# pycsl-expected: PASS
from enum import Enum


class C(Enum):
    _ignore_ = ["tmp"]
    A = 1
    B = 2
    C2 = B

    def describe(self) -> int:
        return 1


#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(2)
    y = C.C2
    z = C.A.value
    return 0


if __name__ == "__main__":
    print(f())
