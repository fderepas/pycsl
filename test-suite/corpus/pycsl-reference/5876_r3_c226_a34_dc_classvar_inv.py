r"""Test 5876 -- driver run #3 route #226 polarity flip (expected FAIL): red team 29 `a34_dc_classvar_inv` — a `ClassVar[int] = -1` read through `self` under `self.k >= 0`. The constructor goal was not stated and every method ASSUMED the invariant (PROVED at 8f4221371; CPython violates). Now the goal is stated (and FAILS) or the class is REFUSED (PYCSL-R226-INVARIANT-GOAL-NOT-STATED).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import ClassVar

#@ class invariant self.k >= 0
@dataclass
class D:
    x: int
    k: ClassVar[int] = -1

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.k

if __name__ == "__main__":
    print(f(D(1)))
