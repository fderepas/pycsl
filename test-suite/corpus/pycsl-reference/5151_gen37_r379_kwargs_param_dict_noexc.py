r"""Test 5151 -- gen #37 route #379 (expected FAIL): `D(**kw)` with `kw: Dict[str, int]` under `no_exception` and `ensures \result == 0` (CPython 3, or TypeError on another key). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Dict

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 0
def f(kw: Dict[str, int]) -> int:
    d = D(**kw)
    return d.x

if __name__ == "__main__":
    print(f({"x": 3}))
