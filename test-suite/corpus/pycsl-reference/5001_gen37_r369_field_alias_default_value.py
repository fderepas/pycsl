r"""Test 5001 -- gen #37 route #369 (expected FAIL): `fld(default=7)` read as default 0 (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field as fld

@dataclass
class D:
    x: int = fld(default=7)

#@ ensures \result == 0
def f() -> int:
    d = D()
    return d.x

if __name__ == "__main__":
    print(f())
