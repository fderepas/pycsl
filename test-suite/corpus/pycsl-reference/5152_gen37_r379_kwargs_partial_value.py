r"""Test 5152 -- gen #37 route #379 (expected FAIL): `D(1, **{"y": 7}).y == 0` (CPython 7). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int
    y: int

#@ ensures \result == 0
def f() -> int:
    kw = {"y": 7}
    d = D(1, **kw)
    return d.y

if __name__ == "__main__":
    print(f())
