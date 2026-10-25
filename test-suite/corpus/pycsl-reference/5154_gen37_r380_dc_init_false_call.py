r"""Test 5154 -- gen #37 route #380 (expected FAIL): `@dataclass(init=False)` called `D(1)` lowered to `{ x = 4 }` (CPython TypeError: `object.__init__` takes no argument). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass(init=False)
class D:
    x: int = 4

#@ no_exception \all
def f() -> int:
    d = D(1)
    return d.x

if __name__ == "__main__":
    print(f())
