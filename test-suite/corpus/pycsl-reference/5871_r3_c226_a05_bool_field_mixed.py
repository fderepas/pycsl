r"""Test 5871 -- driver run #3 route #226 polarity flip (expected FAIL): red team 29 `a05_bool_field_mixed` — `self.x >= 0 or self.ok` over a `@dataclass` int + bool field. The constructor goal was not stated and every method ASSUMED the invariant (PROVED at 8f4221371; CPython violates). Now the goal is stated (and FAILS) or the class is REFUSED (PYCSL-R226-INVARIANT-GOAL-NOT-STATED).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

#@ class invariant self.x >= 0 or self.ok
@dataclass
class D:
    x: int
    ok: bool

#@ ensures \result >= 0
def f(d: D) -> int:
    if d.ok:
        return 0
    return d.x

if __name__ == "__main__":
    print(f(D(-1, False)))
