r"""Test 4991 -- gen #37 route #369 (expected FAIL): `k: CV[int] = 3` (`ClassVar as CV`) taken as a field: `D(1, 5)` admitted (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import ClassVar as CV

@dataclass
class D:
    x: int
    k: CV[int] = 3

#@ no_exception \all
def f() -> int:
    d = D(1, 5)
    return d.x

if __name__ == "__main__":
    print(f())
