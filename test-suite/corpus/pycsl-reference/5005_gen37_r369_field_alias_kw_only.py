r"""Test 5005 -- gen #37 route #369 (expected FAIL): `fld(kw_only=True)` read as positional (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field as fld

@dataclass
class D:
    x: int = fld(default=0, kw_only=True)
    y: int = 0

#@ ensures \result == 5
def f() -> int:
    d = D(5)
    return d.x

if __name__ == "__main__":
    print(f())
