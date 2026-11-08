r"""Test 5874 -- driver run #3 route #226 polarity flip (expected FAIL): red team 29 `a11_default_factory_int_def` — `field(default_factory=int)` int field (an `__init__` argument) under `self.n >= 0`. The constructor goal was not stated and every method ASSUMED the invariant (PROVED at 8f4221371; CPython violates). Now the goal is stated (and FAILS) or the class is REFUSED (PYCSL-R226-INVARIANT-GOAL-NOT-STATED).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

#@ class invariant self.n >= 0
@dataclass
class D:
    x: int
    n: int = field(default_factory=int)

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.n

if __name__ == "__main__":
    print(f(D(1, -3)))
