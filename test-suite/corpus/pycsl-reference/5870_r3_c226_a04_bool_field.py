r"""Test 5870 -- driver run #3 route #226 polarity flip (expected FAIL): red team 29 `a04_bool_field` — a bool FIELD of a `@dataclass` under `self.ok == True`. The constructor goal was not stated and every method ASSUMED the invariant (PROVED at 8f4221371; CPython violates). Now the goal is stated (and FAILS) or the class is REFUSED (PYCSL-R226-INVARIANT-GOAL-NOT-STATED).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

#@ class invariant self.ok == True
@dataclass
class D:
    x: int
    ok: bool

#@ ensures \result == True
def f(d: D) -> bool:
    return d.ok

if __name__ == "__main__":
    print(f(D(1, False)))
