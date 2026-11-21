r"""Test 5033 -- gen #37 route #372 (expected FAIL): `t: Tuple[D, int]`, `{t[0]}` (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Tuple

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(t: Tuple[D, int]) -> int:
    s = {t[0]}
    return 1

if __name__ == "__main__":
    print(g((D(1), 2)))
