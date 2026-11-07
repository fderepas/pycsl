r"""Test 4865 -- gen #37 route #362 (expected FAIL): witness r07: invariant `self.x >= 0` on a `@dataclass` with a defaulted `InitVar`: no constructor goal, invariant assumed; PROVED (CPython -1). REFUSED (PYCSL-R362-INITVAR-INVARIANT, route #362).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, InitVar

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    k: InitVar[int] = 0

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1)) >= 0, f(D(-1))
