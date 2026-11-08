r"""Test 5003 -- gen #37 route #369 (expected FAIL): `fld(init=False, default=4)` takes a positional argument (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field as fld

@dataclass
class D:
    x: int
    y: int = fld(init=False, default=4)

#@ no_exception \all
def f() -> int:
    d = D(1, 2)
    return d.x

if __name__ == "__main__":
    print(f())
