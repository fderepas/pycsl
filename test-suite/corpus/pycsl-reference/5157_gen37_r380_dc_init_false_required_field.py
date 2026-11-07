r"""Test 5157 -- gen #37 route #380 (expected FAIL): `@dataclass(init=False)` with a required field called `D(1)` (CPython TypeError). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass(init=False)
class D:
    x: int

#@ no_exception \all
def f() -> int:
    d = D(1)
    return 1

if __name__ == "__main__":
    print(f())
