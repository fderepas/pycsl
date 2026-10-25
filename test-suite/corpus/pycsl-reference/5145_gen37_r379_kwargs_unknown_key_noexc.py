r"""Test 5145 -- gen #37 route #379 (expected FAIL): `D(**kw)` with an unknown key `z` under `no_exception` (CPython TypeError). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
def f() -> int:
    kw = {"x": 1, "z": 2}
    d = D(**kw)
    return d.x

if __name__ == "__main__":
    print(f())
