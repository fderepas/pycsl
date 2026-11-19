r"""Test 4956 -- gen #37 route #226 (expected FAIL): `@dataclass` `x: int; p: Optional[int]` (an `Optional` field) under `#@ class invariant self.x >= 0`; no goal was stated and `ensures \result >= 0` on `d.x` PROVED (CPython `D(-1, None).x` is -1). The projection states `forall x. x = x -> x >= 0`, which FAILS.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Optional

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    p: Optional[int]

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1, None)) == -1
