r"""Test 4911 -- gen #37 route #365 (expected FAIL): `t: Optional[Tuple[int, D]]; hash(t)` (CPython TypeError). REFUSED now (route #365).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(t: Optional[Tuple[int, D]]) -> int:
    h = hash(t)
    return 1

if __name__ == "__main__":
    print(g((1, D(1))))
