r"""Test 5147 -- gen #37 route #379 (expected FAIL): `D(1, **{"x": 2})` binds `x` twice under `no_exception` (CPython TypeError). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
def f() -> int:
    kw = {"x": 2}
    d = D(1, **kw)
    return d.x

if __name__ == "__main__":
    print(f())
