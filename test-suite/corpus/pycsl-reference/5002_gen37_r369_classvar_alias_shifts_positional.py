r"""Test 5002 -- gen #37 route #369 (expected FAIL): `CV` alias shifts the positional binding (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import ClassVar as CV

@dataclass
class D:
    k: CV[int] = 3
    x: int = 0

#@ ensures \result == 0
def f() -> int:
    d = D(5)
    return d.x

if __name__ == "__main__":
    print(f())
