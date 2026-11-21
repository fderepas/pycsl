r"""Test 5873 -- driver run #3 route #226 polarity flip (expected FAIL): red team 29 `a10_default_factory_int` — `field(default_factory=lambda: -1, init=False)` int field under `self.n >= 0`. The constructor goal was not stated and every method ASSUMED the invariant (PROVED at 8f4221371; CPython violates). Now the goal is stated (and FAILS) or the class is REFUSED (PYCSL-R226-INVARIANT-GOAL-NOT-STATED).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

#@ class invariant self.n >= 0
@dataclass
class D:
    x: int
    n: int = field(default_factory=lambda: -1, init=False)

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.n

if __name__ == "__main__":
    print(f(D(1)))
