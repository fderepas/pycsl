r"""Test 4950 -- gen #37 route #226 (expected FAIL): witness q362str: `@dataclass` `x: int; s: str` under `#@ class invariant self.x >= 0`; the `str` field put the class outside increments 1/2, so NO constructor goal was stated and `ensures \result >= 0` on `d.x` PROVED (CPython `D(-1, "a").x` is -1). Now the goal is stated over the int field the invariant reads (`forall x. x = x -> x >= 0`) and FAILS.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    s: str

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1, "a")) == -1
