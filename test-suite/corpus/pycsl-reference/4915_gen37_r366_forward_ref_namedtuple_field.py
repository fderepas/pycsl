r"""Test 4915 -- gen #37 route #366 (expected FAIL): frozen `A(z: "Z")`, `Z` a NamedTuple with a list field declared AFTER `A`; `{a}` PROVED (CPython TypeError). REFUSED now (route #366: fixpoint).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import NamedTuple, List

@dataclass(frozen=True)
class A:
    z: "Z"

class Z(NamedTuple):
    xs: List[int]

#@ no_exception \all
#@ ensures \result == 1
def g(a: A) -> int:
    s = {a}
    return 1

if __name__ == "__main__":
    print(g(A(Z([1]))))
