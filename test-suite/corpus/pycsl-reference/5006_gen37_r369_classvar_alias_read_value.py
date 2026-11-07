r"""Test 5006 -- gen #37 route #369 (expected FAIL): `CV` alias read as the constructor argument (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import ClassVar as CV

@dataclass
class D:
    x: int
    k: CV[int] = 3

#@ ensures \result == 9
def f() -> int:
    d = D(1, 9)
    return d.k

if __name__ == "__main__":
    print(f())
