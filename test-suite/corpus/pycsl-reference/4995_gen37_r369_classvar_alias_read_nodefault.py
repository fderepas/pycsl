r"""Test 4995 -- gen #37 route #369 (expected FAIL): `k: CV[int]` without value read as a field (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import ClassVar as CV

@dataclass
class D:
    x: int
    k: CV[int]

#@ no_exception \all
def f(d: D) -> int:
    return d.k

if __name__ == "__main__":
    print(f(D(1)))
