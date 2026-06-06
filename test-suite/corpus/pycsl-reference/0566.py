"""Test 0566 — object (class-binder) quantification, value mode (quantification P4 / scc3.md A).

`\forall o: C; o.x >= 0` quantifies over all instances of class `C`. `C` carries a
`#@ class invariant self.x >= 0`, which lowers to a Why3 TYPE invariant on the record
(`type c = { mutable x: int } invariant { x >= 0 }`) — so it holds for every value of
`c`, and the quantified property discharges. The bound record var's field `o.x` lowers
to the record field (scc3.md Phase A: the binder's type is propagated into the body's
attribute lowering), not an abstract getter.

The class invariant is the antecedent FOR FREE (via the Why3 type invariant); no
explicit `inv_C(o) ==>` guard is synthesized. Negative twin 0567 drops the invariant.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x: int = 0


#@ ensures \forall o: C; o.x >= 0
#@ assigns \nothing
def all_c_nonneg() -> int:
    return 0
