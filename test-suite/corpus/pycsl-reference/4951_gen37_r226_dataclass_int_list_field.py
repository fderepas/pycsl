r"""Test 4951 -- gen #37 route #226 (expected FAIL): witness q362list: `@dataclass` `x: int; xs: List[int] = field(default_factory=list)` under `#@ class invariant self.x >= 0`; the `List` field put the class outside increments 1/2 (no goal, `ensures \result >= 0` on `d.x` PROVED; CPython `D(-1).x` is -1). The int-field projection states `forall x. x = x -> x >= 0`, which FAILS.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    xs: List[int] = field(default_factory=list)

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1)) == -1
