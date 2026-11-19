r"""Test 5148 -- gen #37 route #379 (expected FAIL): `D(**{"x": 5}).x == 0` (the mapping dropped; CPython 5). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ ensures \result == 0
def f() -> int:
    kw = {"x": 5}
    d = D(**kw)
    return d.x

if __name__ == "__main__":
    print(f())
