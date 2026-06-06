"""Test 0567 — negative: object quantification WITHOUT a class invariant is unprovable.

`D` has no `#@ class invariant`, so `type d = { mutable x: int }` carries no Why3 type
invariant and ranges over records with any `x` (including negative). Thus
`\forall o: D; o.x >= 0` is NOT provable — the class invariant in the flagship 0566 is
load-bearing (it is what makes the value-mode quantifier sound). Demonstrates P4 value
mode ranges over invariant-satisfying shapes only when an invariant exists.

Committed `# pycsl-expected: FAIL` and STAYS failing.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class D:
    def __init__(self) -> None:
        self.x: int = 0


#@ ensures \forall o: D; o.x >= 0
#@ assigns \nothing
def all_d_nonneg() -> int:
    return 0
