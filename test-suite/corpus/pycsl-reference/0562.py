"""Test 0562 — inductive predicate (inductive.md P1).

`#@ inductive even(n: int)` defines a least-fixpoint relation by Horn-clause rules;
Why3 derives introduction/inversion/induction. `even` is logic-only (usable in
contracts, never executable). Introduction discharges `even(4)`: even(0) → even(2)
→ even(4). Lowers to `inductive even (n: int) = | Even_zero : even 0 | Even_step :
forall m: int. even m -> even (m + 2) end`.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ inductive even(n: int):
#@     rule even_zero: even(0)
#@     rule even_step: \forall m: int; even(m) ==> even(m + 2)


#@ ensures even(4)
#@ assigns \nothing
def check_four() -> int:
    return 0
