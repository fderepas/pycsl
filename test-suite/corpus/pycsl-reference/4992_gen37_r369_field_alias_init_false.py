r"""Test 4992 -- gen #37 route #369 (expected FAIL): `y: int = fld(init=False)` (`field as fld`) read as stored (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field as fld

@dataclass
class D:
    x: int
    y: int = fld(init=False)

#@ no_exception \all
def f(d: D) -> int:
    return d.y

if __name__ == "__main__":
    print(f(D(1)))
