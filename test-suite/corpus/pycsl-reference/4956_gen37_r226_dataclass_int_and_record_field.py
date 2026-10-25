r"""Test 4956 -- gen #37 route #226 (expected FAIL): `@dataclass` `x: int; p: P` (a RECORD-typed field, `P` another dataclass) under `#@ class invariant self.x >= 0`; no goal was stated and `ensures \result >= 0` on `d.x` PROVED (CPython `D(-1, P(0)).x` is -1). The projection states `forall x. x = x -> x >= 0`, which FAILS.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class P:
    v: int

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    p: P

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1, P(0))) == -1
