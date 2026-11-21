r"""Test 4917 -- gen #37 route #366 (expected FAIL): frozen `A(zs: Tuple[Z, int])`, `Z` an eq-dataclass; `{a}` PROVED (CPython TypeError). REFUSED now (route #366).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Z:
    n: int

@dataclass(frozen=True)
class A:
    zs: Tuple[Z, int]

#@ no_exception \all
#@ ensures \result == 1
def g(a: A) -> int:
    s = {a}
    return 1

if __name__ == "__main__":
    print(g(A((Z(1), 2))))
