r"""Test 4914 -- gen #37 route #366 (expected FAIL): `@dataclass(unsafe_hash=True)` with a `List[int]` field; `{d}` PROVED (CPython TypeError). REFUSED now (route #366).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List

@dataclass(unsafe_hash=True)
class D:
    xs: List[int] = field(default_factory=list)

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D([1])))
